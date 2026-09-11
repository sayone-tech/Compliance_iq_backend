#!/usr/bin/env python3
"""Extract a WSP manual PDF to normalised text with page markers.

The plan for this POC assumed the two sample files were plain text with a
misleading .pdf extension. They are not -- both are real, text-native PDFs
(`Sample WSP.pdf` 154pp untagged PDFium; `WSP Sample.pdf` 199pp tagged Word
2007). Neither needs OCR, so this stage is a poppler `pdftotext -layout` call
plus the normalisation pass the extraction analysis calls mandatory
(docs/research/WSP Analysis/wsp-analysis/sample-wsp-extraction-analysis.md,
section 1, implication 4).

Page provenance survives extraction as `[[page:N]]` marker lines, one per form
feed. Everything downstream (chunk provenance, FR-31 "pages 12-15 cover Art.
92" citations) keys on those.

Usage, from the repository root:

    python3 scripts/wsp_poc/extract_wsp.py \
        --pdf "docs/research/WSP Analysis/Sample WSP.pdf" \
        --out out/wsp/sample_wsp.txt --with-synthetic

    python3 scripts/wsp_poc/extract_wsp.py \
        --pdf "docs/research/WSP Analysis/WSP Sample.pdf" \
        --out out/wsp/triad_wsp.txt

--with-synthetic appends the fixture sections in synthetic_sections.txt, which
are deliberately drafted to satisfy DORA Art. 11, DORA Art. 17 and MiCA Art. 70.
Without them the golden set has no true positives -- both real samples are US
FINRA manuals and score gap-heavy against MiCA/DORA by construction.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SYNTHETIC_PATH = os.path.join(HERE, "synthetic_sections.txt")

# Mojibake seen in the two samples: Word 2007 smart quotes arriving through a
# non-embedded Times New Roman cmap, and SymbolMT bullets with no ToUnicode map.
MOJIBAKE = {
    "‖": '"',   # ‖  250x in WSP Sample.pdf
    "―": '"',   # ―  245x
    "‘": "'",   # ‘  359x
    "’": "'",
    "“": '"',
    "”": '"',
    "∑": "•",  # ∑  16x in Sample WSP.pdf -- a mis-mapped bullet
    "–": "-",
    "—": "-",
    "": "•",
    "ﬁ": "fi",
    "ﬂ": "fl",
}

# Printed footers: "- 42 -" (Triad) and bare centred integers (WealthForge).
FOOTER_RE = re.compile(r"^\s*(?:-\s*\d{1,4}\s*-|\d{1,4}|Page\s+\d{1,4}(?:\s+of\s+\d{1,4})?)\s*$",
                       re.IGNORECASE)
# "20.1.1In General" -> "20.1.1 In General"
GLUED_RE = re.compile(r"(\d)([A-Z][a-z])")
# "gratuity.44 The firm" -> "gratuity. The firm"; footnote markers glued to words.
FOOTNOTE_RE = re.compile(r"(?<=[a-z])\.(\d{1,3})(?=\s+[A-Z])")


def extract_pdf(pdf_path):
    """Text-native extraction via poppler. Returns one string per page."""
    if not shutil.which("pdftotext"):
        raise SystemExit("pdftotext not found -- install poppler-utils "
                         "(sudo apt install poppler-utils)")
    proc = subprocess.run(
        ["pdftotext", "-layout", "-enc", "UTF-8", pdf_path, "-"],
        capture_output=True, check=True,
    )
    raw = proc.stdout.decode("utf-8", errors="replace")
    return raw.split("\f")


def normalise(text):
    for bad, good in MOJIBAKE.items():
        text = text.replace(bad, good)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = []
    for line in text.split("\n"):
        line = line.rstrip()
        if FOOTER_RE.match(line):
            continue
        # De-glue only where a numbering prefix has swallowed the title.
        if re.match(r"^\s*\d+(\.\d+)*[A-Z]", line):
            line = GLUED_RE.sub(r"\1 \2", line, count=1)
        line = FOOTNOTE_RE.sub(".", line)
        lines.append(line)
    text = "\n".join(lines)
    # Collapse runs of blank lines; keep paragraph boundaries.
    text = re.sub(r"\n{3,}", "\n\n", text)
    # -layout pads with long runs of spaces; keep two as a weak column signal.
    text = re.sub(r"[ \t]{3,}", "  ", text)
    return text


def build_document(pdf_path, with_synthetic=False):
    pages = extract_pdf(pdf_path)
    out = []
    for number, page in enumerate(pages, start=1):
        body = normalise(page).strip()
        if not body:
            continue
        out.append(f"[[page:{number}]]\n{body}")
    doc = "\n\n".join(out)
    if with_synthetic:
        with open(SYNTHETIC_PATH, encoding="utf-8") as handle:
            fixture = handle.read().strip()
        doc += f"\n\n[[page:{len(pages) + 1}]]\n{fixture}\n"
    return doc, len(pages)


def main():
    parser = argparse.ArgumentParser(
        description="Extract a WSP PDF to normalised text with [[page:N]] markers.")
    parser.add_argument("--pdf", required=True, help="path to the WSP PDF")
    parser.add_argument("--out", required=True, help="path to write the text to")
    parser.add_argument("--with-synthetic", action="store_true",
                        help="append the DORA 11 / DORA 17 / MiCA 70 fixture sections")
    args = parser.parse_args()

    doc, pages = build_document(args.pdf, args.with_synthetic)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as handle:
        handle.write(doc)
    words = len(doc.split())
    print(f"{args.pdf}: {pages} pages -> {args.out} "
          f"({words:,} words, ~{words * 4 // 3:,} tokens)"
          f"{' + synthetic fixture' if args.with_synthetic else ''}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
