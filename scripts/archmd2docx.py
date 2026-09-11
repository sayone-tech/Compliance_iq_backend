#!/usr/bin/env python3
"""Render a tech-spec Markdown source to .docx in the ControlIQ System
Architecture house style.

Usage, from the repository root:

    python3 scripts/archmd2docx.py \\
        docs/tech-spec/ControlIQ_Architecture_Review_Responses.md \\
        docs/tech-spec/ControlIQ_Architecture_Review_Responses.docx

The System Architecture .docx is used as the style template: its styles.xml
(Calibri body, 1F3B63 headings, 4F81BD Heading 3), page setup and headers are
inherited, so the response document sits beside it without a visual seam. The
template's body content is cleared and rebuilt from the Markdown; only the
running header text is rewritten, from the `Header:` line below the title.

The PRD has its own converter (scripts/md2docx.py) with colour-coded annotation
chips. This one is deliberately plainer: headings, paragraphs, bullets, tables
and inline `**bold**`/`*italic*`/`` `code` ``.

Requires python-docx.
"""
import re
import sys
import zipfile

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Pt, RGBColor

TEMPLATE = 'docs/tech-spec/ControlIQ_System_Architecture.docx'
HEADER_FILL = '1F3B63'          # table header row, matching Heading 1
TITLE_COLOUR = '17365D'
RULE_COLOUR = '4F81BD'

INLINE = re.compile(
    r'(`[^`]+`|\*\*\*.+?\*\*\*|\*\*.+?\*\*|\*[^*]+?\*|<br\s*/?>)')


def shade(cell, fill):
    cell._tc.get_or_add_tcPr().append(
        parse_xml(f'<w:shd {nsdecls("w")} w:val="clear" w:fill="{fill}"/>'))


def tokenize(text, bold=False, italic=False):
    """Yield (text, bold, italic, is_code) for markdown inline spans."""
    for part in INLINE.split(text):
        if not part:
            continue
        if re.match(r'^<br\s*/?>$', part):
            yield (None, bold, italic, False)
        elif part.startswith('`') and part.endswith('`'):
            yield (part[1:-1], bold, italic, True)
        elif part.startswith('***') and part.endswith('***') and len(part) > 6:
            yield from tokenize(part[3:-3], True, True)
        elif part.startswith('**') and part.endswith('**') and len(part) > 4:
            yield from tokenize(part[2:-2], True, italic)
        elif part.startswith('*') and part.endswith('*') and len(part) > 2:
            yield from tokenize(part[1:-1], bold, True)
        else:
            yield (part, bold, italic, False)


def emit(par, text):
    for txt, bold, italic, code in tokenize(text.replace(r'\|', '|')):
        if txt is None:                      # <br> -- a soft line break
            par.add_run().add_break(WD_BREAK.LINE)
            continue
        run = par.add_run(txt)
        run.bold = bold
        run.italic = italic
        if code:
            run.font.name = 'Consolas'
            run.font.size = Pt(9)


def column_widths(cells, ncols, total):
    """Split the usable page width across columns in proportion to how much
    text each holds, so a six-column table does not give the recommendation
    column the same room as the two-character ID column. Square-rooted to damp
    the extremes, and floored so no column collapses."""
    weights = []
    for j in range(ncols):
        longest = max(
            (len(row[j]) for row in cells if j < len(row)), default=1)
        weights.append(max(longest, 6) ** 0.5)
    scale = total / sum(weights)
    floor = total // (ncols * 3)
    return [max(int(w * scale), floor) for w in weights]


def add_table(doc, rows, usable_width):
    cells = [
        [c.strip() for c in re.split(r'(?<!\\)\|', r)[1:-1]]
        for r in rows
    ]
    ncols = max(len(r) for r in cells)
    table = doc.add_table(rows=len(cells), cols=ncols)
    table.style = 'Table Grid'
    table.autofit = False
    widths = column_widths(cells, ncols, usable_width)
    for j, width in enumerate(widths):
        table.columns[j].width = width      # w:gridCol -- what Word lays out on
        for row in table.rows:
            row.cells[j].width = width      # w:tcW -- what LibreOffice reads
    for i, row in enumerate(cells):
        for j in range(ncols):
            cell = table.rows[i].cells[j]
            cell.paragraphs[0].text = ''
            emit(cell.paragraphs[0], row[j] if j < len(row) else '')
            if i == 0:
                shade(cell, HEADER_FILL)
                for run in cell.paragraphs[0].runs:
                    run.bold = True
                    run.font.color.rgb = RGBColor.from_string('FFFFFF')
    doc.add_paragraph()


def blank_template():
    """A Document with the architecture doc's styles and page setup, but no
    body content -- the trailing sectPr (page size, margins, header refs) is
    kept so headers and layout carry over."""
    doc = Document(TEMPLATE)
    body = doc.element.body
    for child in list(body):
        if child.tag != qn('w:sectPr'):
            body.remove(child)
    return doc


def set_header(doc, text):
    for section in doc.sections:
        for hdr in (section.header, section.first_page_header,
                    section.even_page_header):
            for par in hdr.paragraphs:
                if par.runs:
                    par.runs[0].text = text
                    for extra in par.runs[1:]:
                        extra.text = ''
                    break


def prune_unused_media(docx_path):
    """Drop images inherited from the template that this document never
    references -- the architecture diagram alone is ~280 KB -- along with their
    now-dangling relationships."""
    with zipfile.ZipFile(docx_path) as zf:
        parts = {n: zf.read(n) for n in zf.namelist()}

    body = parts['word/document.xml'].decode('utf-8')
    used = set(re.findall(r'r:(?:embed|id)="([^"]+)"', body))
    rels_name = 'word/_rels/document.xml.rels'
    rels = parts[rels_name].decode('utf-8')

    dropped_targets = set()

    def keep(match):
        rel = match.group(0)
        rid = re.search(r'Id="([^"]+)"', rel).group(1)
        target = re.search(r'Target="([^"]+)"', rel).group(1)
        if 'media/' in target and rid not in used:
            dropped_targets.add('word/' + target.lstrip('/'))
            return ''
        return rel

    rels = re.sub(r'<Relationship [^>]*/>', keep, rels)
    if not dropped_targets:
        return

    parts[rels_name] = rels.encode('utf-8')
    for target in dropped_targets:
        parts.pop(target, None)

    with zipfile.ZipFile(docx_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for name, data in parts.items():
            zf.writestr(name, data)


def convert(md_path, docx_path):
    lines = open(md_path, encoding='utf-8').read().splitlines()
    doc = blank_template()

    i = 0
    if lines and lines[0].lstrip().startswith('<!--'):  # md-only header comment
        while i < len(lines) and '-->' not in lines[i]:
            i += 1
        i += 1

    sec = doc.sections[0]
    usable = sec.page_width - sec.left_margin - sec.right_margin

    header_text = None
    first_heading = True

    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue

        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            text = line.lstrip('#').strip()
            if level == 1 and first_heading:
                # Title block: the document name, centred, rule beneath.
                par = doc.add_paragraph()
                par.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = par.add_run(text)
                run.bold = True
                run.font.size = Pt(20)
                run.font.color.rgb = RGBColor.from_string(TITLE_COLOUR)
                par.paragraph_format.space_after = Pt(4)
                par._p.get_or_add_pPr().append(parse_xml(
                    f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" '
                    f'w:sz="8" w:space="4" w:color="{RULE_COLOUR}"/></w:pBdr>'))
                first_heading = False
            else:
                doc.add_heading(text, level=min(level, 4))
            i += 1
            continue

        if line.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                if not re.match(r'^\|[\s:|-]+\|$', lines[i]):
                    rows.append(lines[i])
                i += 1
            add_table(doc, rows, usable)
            continue

        if line.startswith('- '):
            emit(doc.add_paragraph(style='List Bullet'), line[2:].strip())
            i += 1
            continue

        if re.match(r'^\d+\. ', line):
            emit(doc.add_paragraph(style='List Number'),
                 re.sub(r'^\d+\. ', '', line).strip())
            i += 1
            continue

        text = line.strip()
        if header_text is None and text.startswith('Header:'):
            header_text = text[len('Header:'):].strip()
            i += 1
            continue
        emit(doc.add_paragraph(), text)
        i += 1

    if header_text:
        set_header(doc, header_text)
    doc.save(docx_path)
    prune_unused_media(docx_path)
    print(f'wrote {docx_path}')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    convert(sys.argv[1], sys.argv[2])
