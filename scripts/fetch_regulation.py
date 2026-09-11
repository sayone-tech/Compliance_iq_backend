#!/usr/bin/env python3
"""Spike: fetch DORA and MiCA from CELLAR and parse the Formex XML into
article-level records.

This is the spike the regulation-ingest workflow calls for before the real
pipeline is built ("run fetch_formex against the real endpoint before
finalising the parser"). It only reads from the Publications Office; it writes
nothing unless --json or --raw-dir is given.

Usage, from the repository root:

    python3 scripts/fetch_regulation.py                        # both acts, summary
    python3 scripts/fetch_regulation.py --celex 32022R2554     # one act
    python3 scripts/fetch_regulation.py --celex 32022R2554 --article 17
    python3 scripts/fetch_regulation.py --json out/            # dump records
    python3 scripts/fetch_regulation.py --raw-dir out/raw/     # archive XML parts
    python3 scripts/fetch_regulation.py --check-amendments     # SPARQL poll
    python3 scripts/fetch_regulation.py --celex 02023R1114-20240109   # consolidated

The plain CELEX numbers return the text as first published in the Official
Journal. The 0-prefixed form with a date returns a consolidated expression --
the amended text as it stood on that date, root <CONS.ACT> -- which is what a
change-detection diff should actually compare.

Requires requests and lxml.

Notes from running this against the live endpoint (2026-09-07):

  * The default python-requests User-Agent gets HTTP 403 from
    publications.europa.eu -- an explicit User-Agent is mandatory, not polite.
  * The zip carries a small `*.doc.xml` metadata wrapper (root <DOC>) plus the
    real content parts: root <ACT> for the enacting terms, root <ANNEX> for
    each annex. There is no toc.xml member.
  * <?PAGE NO="40"?> processing instructions are not emitted by itertext(), so
    the normalised text -- and therefore the content hash -- stays clean.
  * The in-force date is not carried in Formex. Only the OJ publication date
    and the signature date are, so in_force_date stays None here; the real
    pipeline takes it from CDM/ELI metadata (see
    docs/research/WSP Analysis/regulatory/regulatory-ingestion.md, section 1.1).
"""
import argparse
import hashlib
import io
import json
import os
import sys
import time
import zipfile
from dataclasses import asdict, dataclass, field

import requests
from lxml import etree

CELLAR_URL = "http://publications.europa.eu/resource/celex/{celex}"
SPARQL_URL = "https://publications.europa.eu/webapi/rdf/sparql"

# The tracked-acts list is configuration, not code: adding a newly adopted
# RTS/ITS means adding its CELEX number here.
TRACKED = {
    "32022R2554": "DORA",
    "32023R1114": "MiCA",
}

HEADERS = {
    "Accept": "application/zip;mtype=fmx4, application/xml;mtype=fmx4",
    "Accept-Language": "eng",
    # Without a User-Agent of our own, CELLAR answers 403.
    "User-Agent": "ControlIQ-regulation-ingest-spike/0.1 (+sayonetech.com)",
}

# Amending / correcting acts touching the tracked regulations.
AMENDMENT_QUERY = """
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT DISTINCT ?celex WHERE {
  VALUES ?base_id { %s }
  ?base cdm:resource_legal_id_celex ?base_id .
  { ?act cdm:resource_legal_amends_resource_legal ?base }
  UNION
  { ?act cdm:resource_legal_corrects_resource_legal ?base }
  ?act cdm:resource_legal_id_celex ?celex .
}
"""


# --------------------------------------------------------------------------
# records


@dataclass
class Paragraph:
    paragraph_id: str   # Formex IDENTIFIER, e.g. "017.001"
    number: str         # "1."
    text: str
    content_hash: str


@dataclass
class ArticleRecord:
    celex: str
    short_name: str
    part: str           # zip member the record came from
    article_id: str     # Formex IDENTIFIER, e.g. "017"
    label: str          # "Article 17"
    heading: str | None  # "ICT-related incident management process"
    chapter_path: list  # ["TITLE III ...", "CHAPTER I ..."]
    text: str
    content_hash: str   # SHA-256 of text -- the change-detection primitive
    paragraphs: list = field(default_factory=list)


@dataclass
class AnnexRecord:
    celex: str
    short_name: str
    part: str
    label: str          # "ANNEX I"
    heading: str | None
    text: str
    content_hash: str


# --------------------------------------------------------------------------
# fetch


def fetch_formex(celex, retries=3):
    """Fetch the Formex manifestation(s) for a CELEX number.

    CELLAR content-negotiates and returns either a zip of parts or a single
    XML file. Returns a list of (part_name, xml_bytes).
    """
    url = CELLAR_URL.format(celex=celex)
    delay = 2
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=90, allow_redirects=True)
            if resp.status_code >= 500:
                raise requests.HTTPError(f"{resp.status_code} from {resp.url}")
            resp.raise_for_status()
            break
        except (requests.Timeout, requests.ConnectionError, requests.HTTPError) as exc:
            if attempt == retries:
                raise
            print(f"  ! fetch attempt {attempt} failed ({exc}); retrying in {delay}s",
                  file=sys.stderr)
            time.sleep(delay)
            delay *= 2

    content_type = resp.headers.get("Content-Type", "")
    if "zip" in content_type:
        zf = zipfile.ZipFile(io.BytesIO(resp.content))
        return [(name, zf.read(name)) for name in zf.namelist()
                if name.lower().endswith(".xml")]
    return [(f"{celex}.xml", resp.content)]


# --------------------------------------------------------------------------
# parse


def _plain_text(el):
    """Normalised plain text of an element: the hashing input."""
    return " ".join(" ".join(el.itertext()).split())


def _sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _chapter_path(article):
    """Titles of the DIVISION ancestors, outermost first.

    Articles sit inside nested <DIVISION> elements whose first child <TITLE>
    holds "TITLE V ..." / "CHAPTER 2 ...".
    """
    path = []
    for anc in article.iterancestors():
        if anc.tag != "DIVISION":
            continue
        title = anc.find("TITLE")
        if title is not None:
            path.append(_plain_text(title))
    return list(reversed(path))


def _parse_paragraphs(article):
    paragraphs = []
    for parag in article.findall("PARAG"):
        no = parag.find("NO.PARAG")
        text = _plain_text(parag)
        paragraphs.append(Paragraph(
            paragraph_id=parag.get("IDENTIFIER", ""),
            number=_plain_text(no) if no is not None else "",
            text=text,
            content_hash=_sha256(text),
        ))
    return paragraphs


def parse_articles(root, celex, part_name):
    records = []
    for art in root.iter("ARTICLE"):
        # Amending acts quote the text they replace inside QUOT.S blocks; those
        # nested articles belong to the amended act, not this one.
        if any(anc.tag in ("QUOT.S", "QUOT.START") for anc in art.iterancestors()):
            print(f"  ! skipping ARTICLE {art.get('IDENTIFIER')} nested in a quoted "
                  f"amendment block ({part_name})", file=sys.stderr)
            continue
        ti = art.find("TI.ART")
        sti = art.find("STI.ART")
        text = _plain_text(art)
        records.append(ArticleRecord(
            celex=celex,
            short_name=TRACKED.get(celex, celex),
            part=part_name,
            article_id=art.get("IDENTIFIER", ""),
            label=_plain_text(ti) if ti is not None else "",
            heading=_plain_text(sti) if sti is not None else None,
            chapter_path=_chapter_path(art),
            text=text,
            content_hash=_sha256(text),
            paragraphs=_parse_paragraphs(art),
        ))
    return records


def parse_annex(el, celex, part_name):
    """Annexes carry different tags than articles, so they get their own shape.

    `el` is a standalone <ANNEX> part root (original acts, one annex per zip
    member) or a <CONS.ANNEX> element inside a consolidated act.
    """
    title = el.find("TITLE")
    contents = el.find("CONTENTS")
    heading = None
    if contents is not None:
        sub = contents.find(".//TITLE")
        if sub is not None:
            heading = _plain_text(sub)
    text = _plain_text(contents if contents is not None else el)
    return AnnexRecord(
        celex=celex,
        short_name=TRACKED.get(celex, celex),
        part=part_name,
        label=_plain_text(title) if title is not None else part_name,
        heading=heading,
        text=text,
        content_hash=_sha256(text),
    )


def parse_doc_metadata(root):
    """OJ identity and dates from the <DOC> wrapper part."""
    meta = {
        "oj_collection": None,
        "oj_number": None,
        "publication_date": None,   # OJ publication
        "signature_date": None,     # date the act was signed
        "in_force_date": None,      # not in Formex -- comes from CDM/ELI metadata
        "title": None,
    }
    pub = root.find("PUBLICATION.REF")
    if pub is not None:
        coll = pub.find("COLL")
        no_oj = pub.find("NO.OJ")
        date = pub.find("DATE")
        meta["oj_collection"] = _plain_text(coll) if coll is not None else None
        meta["oj_number"] = _plain_text(no_oj) if no_oj is not None else None
        if date is not None:
            meta["publication_date"] = date.get("ISO")
    main = root.find(".//DOC.MAIN.PUB")
    if main is not None:
        date = main.find("DATE")
        if date is not None:
            meta["signature_date"] = date.get("ISO")
    title = root.find(".//TITLE")
    if title is not None:
        meta["title"] = _plain_text(title)
    return meta


def parse_consolidation_info(root):
    """Consolidation stamps from <INFO.CONSLEG> in a consolidated act.

    A consolidated expression (CELEX 0-prefixed, e.g. 02023R1114-20240109) is
    the amended text as it stood on START.DATE -- this is what the diff engine
    should compare across runs.
    """
    info = root.find("INFO.CONSLEG")
    if info is None:
        return {}
    return {
        "consolidation_ref": info.get("CONSLEG.REF"),
        "consolidation_date": info.get("CONSLEG.DATE"),
        "last_modified": info.get("DATE.LAST.MOD"),
        "expression_start_date": info.get("START.DATE"),
        "expression_end_date": info.get("END.DATE"),
    }


def parse_act(celex, parts):
    """Parse every zip part of one act into {metadata, articles, annexes}."""
    metadata, articles, annexes = {}, [], []
    for part_name, xml_bytes in parts:
        root = etree.fromstring(xml_bytes)
        if root.tag == "DOC":
            metadata.update(parse_doc_metadata(root))
        elif root.tag in ("ACT", "CONS.ACT"):
            articles.extend(parse_articles(root, celex, part_name))
            # A consolidated act keeps its annexes inline as <CONS.ANNEX>
            # instead of shipping them as separate zip members.
            for annex in root.iter("CONS.ANNEX"):
                annexes.append(parse_annex(annex, celex, part_name))
            if root.tag == "CONS.ACT":
                metadata.update(parse_consolidation_info(root))
        elif root.tag == "ANNEX":
            annexes.append(parse_annex(root, celex, part_name))
        else:
            print(f"  ! unexpected root <{root.tag}> in {part_name}", file=sys.stderr)
    return metadata, articles, annexes


# --------------------------------------------------------------------------
# amendment detection


def check_amendments(celex_numbers):
    values = " ".join(f'"{c}"^^xsd:string' for c in celex_numbers)
    resp = requests.get(
        SPARQL_URL,
        params={"query": AMENDMENT_QUERY % values},
        headers={"Accept": "application/sparql-results+json",
                 "User-Agent": HEADERS["User-Agent"]},
        timeout=60,
    )
    resp.raise_for_status()
    found = sorted({b["celex"]["value"] for b in resp.json()["results"]["bindings"]})
    print(f"amending / correcting acts for {', '.join(celex_numbers)}:")
    if not found:
        print("  (none)")
    for celex in found:
        print(f"  {celex}")
    return found


# --------------------------------------------------------------------------
# output


def print_summary(celex, metadata, articles, annexes, parts):
    name = TRACKED.get(celex, celex)
    print(f"\n=== {name} ({celex}) ===")
    print(f"  {metadata.get('title') or '(no title in metadata)'}"[:160])
    print(f"  OJ {metadata.get('oj_collection')} {metadata.get('oj_number')} · "
          f"published {metadata.get('publication_date')} · "
          f"signed {metadata.get('signature_date')} · "
          f"in force {metadata.get('in_force_date') or 'n/a in Formex'}")
    if metadata.get("expression_start_date"):
        print(f"  consolidated expression: text as it stood on "
              f"{metadata['expression_start_date']} "
              f"(consolidated {metadata.get('consolidation_date')})")
    print(f"  parts: {len(parts)} · articles: {len(articles)} · annexes: {len(annexes)}")
    if articles:
        print(f"  article ids: {articles[0].article_id} .. {articles[-1].article_id}")
        print(f"\n  {'id':>5}  {'label':<12} {'heading':<52} {'chars':>6}  hash")
        preview = articles[:5] + ([None] + articles[-2:] if len(articles) > 7 else [])
        for rec in preview:
            if rec is None:
                print(f"  {'...':>5}")
                continue
            heading = (rec.heading or "")[:50]
            print(f"  {rec.article_id:>5}  {rec.label:<12} {heading:<52} "
                  f"{len(rec.text):>6}  {rec.content_hash[:12]}")
    for annex in annexes:
        print(f"  {annex.label:<12} {(annex.heading or '')[:60]:<62} "
              f"{len(annex.text):>6}  {annex.content_hash[:12]}")


def print_article(articles, wanted):
    """Print one article in full: the record the review queue would receive."""
    key = wanted.lstrip("0").lower()
    for rec in articles:
        if rec.article_id.lstrip("0") == key or rec.label.lower() == f"article {key}":
            print(f"\n{rec.label} — {rec.heading or ''}")
            print(f"  celex        {rec.celex} ({rec.short_name})")
            print(f"  article_id   {rec.article_id}")
            print(f"  chapter      {' > '.join(rec.chapter_path) or '(none)'}")
            print(f"  content_hash {rec.content_hash}")
            print(f"  paragraphs   {len(rec.paragraphs)}")
            for para in rec.paragraphs:
                print(f"\n  [{para.paragraph_id}] {para.text}")
            if not rec.paragraphs:
                print(f"\n  {rec.text}")
            return True
    print(f"  ! article {wanted} not found", file=sys.stderr)
    return False


def dump_json(out_dir, celex, metadata, articles, annexes):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{celex}.json")
    payload = {
        "celex": celex,
        "short_name": TRACKED.get(celex, celex),
        "metadata": metadata,
        "articles": [asdict(a) for a in articles],
        "annexes": [asdict(a) for a in annexes],
    }
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
    print(f"  wrote {path}")


def archive_raw(raw_dir, celex, parts):
    target = os.path.join(raw_dir, celex)
    os.makedirs(target, exist_ok=True)
    for part_name, xml_bytes in parts:
        path = os.path.join(target, os.path.basename(part_name))
        with open(path, "wb") as handle:
            handle.write(xml_bytes)
    print(f"  archived {len(parts)} part(s) to {target}/")


# --------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Fetch DORA/MiCA Formex XML from CELLAR and parse it into articles.")
    parser.add_argument("--celex", action="append",
                        help="CELEX number to fetch (repeatable; default: all tracked acts)")
    parser.add_argument("--article", help="print this article number in full")
    parser.add_argument("--json", metavar="DIR", help="dump parsed records as JSON into DIR")
    parser.add_argument("--raw-dir", metavar="DIR", help="archive the fetched XML parts into DIR")
    parser.add_argument("--check-amendments", action="store_true",
                        help="SPARQL poll for acts amending or correcting the tracked acts")
    args = parser.parse_args()

    celex_numbers = args.celex or list(TRACKED)

    if args.check_amendments:
        check_amendments(celex_numbers)
        return 0

    for celex in celex_numbers:
        print(f"\nfetching {TRACKED.get(celex, celex)} ({celex}) ...", file=sys.stderr)
        parts = fetch_formex(celex)
        metadata, articles, annexes = parse_act(celex, parts)
        if args.raw_dir:
            archive_raw(args.raw_dir, celex, parts)
        if args.article:
            print_article(articles, args.article)
        else:
            print_summary(celex, metadata, articles, annexes, parts)
        if args.json:
            dump_json(args.json, celex, metadata, articles, annexes)
    return 0


if __name__ == "__main__":
    sys.exit(main())
