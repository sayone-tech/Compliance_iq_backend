#!/usr/bin/env python3
"""Regenerate the WSP Validation Engine blueprint .pdf from its Markdown source.

The Markdown is authoritative; the PDF is the shareable rendering of it. Section
numbering drives the contents rail, and the claim-taxonomy labels (VERIFIED
FACT, ASSUMPTION, ...) are re-chipped so they read the same as in the published
Artifact. Styling lives in scripts/blueprint.css alongside this file.

Usage, from the repository root:

    python3 scripts/blueprint2pdf.py \
        "docs/research/WSP Analysis/continuous_wsp_regulatory_compliance_platform.md" \
        "docs/research/WSP Analysis/continuous_wsp_regulatory_compliance_platform.pdf"

Requires python-markdown and google-chrome (used headless to print).
"""
import html
import io
import os
import re
import subprocess
import sys
import tempfile

import markdown

CLAIM_LABELS = [
    ("REQUIRES LEGAL / COMPLIANCE INTERPRETATION", "legal"),
    ("REQUIRES LEGAL INTERPRETATION", "legal"),
    ("REQUIRES LEGAL REVIEW", "legal"),
    ("ARCHITECTURAL RECOMMENDATION", "rec"),
    ("VERIFIED FACT", "verified"),
    ("VERIFIED", "verified"),
    ("ASSUMPTION", "assume"),
    ("OPEN QUESTION", "open"),
]

FONTS = (
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Spectral:ital,wght@0,400;0,600;0,700;1,400&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&family=IBM+Plex+Mono:wght@400;500;600&display=swap">'
)

PAGE = """<title>{title}</title>
{fonts}
<style>{css}</style>
<div class="shell">
<nav class="rail" aria-label="Contents">
  <p class="raileyebrow">Technical Blueprint</p>
  <p class="railtitle">{railtitle}</p>
  <p class="railmeta">{railmeta}</p>
  <ol class="toc">{toc}</ol>
</nav>
<main class="doc">
<header class="masthead">{masthead}</header>
{body}
</main>
</div>
"""


def chipify(fragment):
    """Wrap the claim-taxonomy labels in styled chips, longest label first."""
    for label, kind in CLAIM_LABELS:
        fragment = re.sub(
            r"(?<![\w>-])" + re.escape(label) + r"(?![\w-])",
            '<span class="claim claim-%s">%s</span>' % (kind, label),
            fragment,
        )
    return fragment


def build_toc(body):
    items = []
    for anchor, text in re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body, re.S):
        text = re.sub(r"<[^>]+>", "", text).strip()
        num, _, label = text.partition(". ")
        items.append(
            '<li><a href="#%s"><span class="tocnum">%s</span>'
            '<span class="toclabel">%s</span></a></li>'
            % (anchor, html.escape(num), html.escape(label or text))
        )
    return "\n".join(items)


def render(md_path):
    text = io.open(md_path, encoding="utf-8").read()
    title = re.match(r"# (.+)", text).group(1)
    version = re.search(r"\*\*Version:\*\* ([\d.]+) · \*\*Date:\*\* ([\d-]+)", text)

    # Split the front matter (everything before "## 1.") from the numbered body.
    split_at = text.index("\n## 1. ")
    head_md = text[text.index("\n", 0) + 1 : split_at].strip()
    head_md = head_md.rstrip("-").rstrip()
    body_md = text[split_at:]

    conv = markdown.Markdown(extensions=["tables", "attr_list", "toc", "sane_lists"])
    masthead = "<h1>%s</h1>\n%s" % (html.escape(title), conv.convert(head_md))
    conv.reset()
    body = conv.convert(body_md)

    masthead, body = chipify(masthead), chipify(body)
    # Tables need a scroll wrapper on narrow screens; print CSS unwraps them.
    masthead, body = (
        re.sub(r"<table>", '<div class="tablewrap"><table>', f).replace(
            "</table>", "</table></div>"
        )
        for f in (masthead, body)
    )

    railtitle = html.escape(title.split(" — ")[0])
    railmeta = "v%s · %s<br>MiCA (EU) 2023/1114 · DORA (EU) 2022/2554" % (
        version.group(1),
        version.group(2),
    )
    here = os.path.dirname(os.path.abspath(__file__))
    return PAGE.format(
        title=html.escape(title.split(" — ")[0]),
        fonts=FONTS,
        css=io.open(os.path.join(here, "blueprint.css"), encoding="utf-8").read(),
        railtitle=railtitle,
        railmeta=railmeta,
        toc=build_toc(body),
        masthead=masthead,
        body=body,
    )


def main():
    md_path, pdf_path = sys.argv[1], sys.argv[2]
    # Chrome needs a file:// URL, so the intermediate HTML goes to a temp dir
    # rather than next to the PDF inside docs/.
    with tempfile.TemporaryDirectory() as tmp:
        html_path = os.path.join(tmp, "blueprint.html")
        io.open(html_path, "w", encoding="utf-8").write(render(md_path))
        subprocess.run(
            [
                "google-chrome",
                "--headless",
                "--disable-gpu",
                "--no-sandbox",
                "--virtual-time-budget=20000",
                "--no-pdf-header-footer",
                "--print-to-pdf=" + os.path.abspath(pdf_path),
                "file://" + html_path,
            ],
            check=True,
            capture_output=True,
        )
    print("wrote %s (%d bytes)" % (pdf_path, os.path.getsize(pdf_path)))


if __name__ == "__main__":
    main()
