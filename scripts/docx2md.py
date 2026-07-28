#!/usr/bin/env python3
"""Convert the ComplianceIQ PRD .docx to Markdown, preserving the colour/shading
semantics the document's own annotation legend relies on.

Usage, from the repository root:

    python3 scripts/docx2md.py \\
        docs/requirement-specification/PRD_v4.docx \\
        docs/requirement-specification/PRD_v4.md

The .docx stays the signed baseline; the Markdown is a derived, diffable mirror.
Re-run this whenever a new PRD revision lands, then re-add the header comment at
the top of the .md (it explains the colour-to-text encoding to readers).

Stdlib only — no pandoc, python-docx, or mammoth required.
"""
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

# Run colours -> what the legend says they mean.
COLOUR_LABEL = {
    '1155cc': '25 Jun FRD call',
    'c55a11': "Sosinna's Drive comment",
    '595959': 'status note',
    '808080': 'status note',
}
# Cell fills -> callout kind.
FILL_CALLOUT = {
    'e2efda': ('CONFIRMED', 'green — agreed decision'),
    'fff2cc': ('OPEN QUESTION', 'amber — unresolved'),
    'ededed': ('DEVELOPER NOTE', 'grey'),
    'ddebf7': ('NOTE', 'blue'),
    'fce4d6': ('NOTE', 'orange'),
}
HEADER_FILL = '1f4e79'


def esc(t):
    return t.replace('|', r'\|')


def run_text(run):
    out = []
    for n in run.iter():
        tag = n.tag
        if tag == W + 't':
            out.append(n.text or '')
        elif tag == W + 'tab':
            out.append(' ')
        elif tag in (W + 'br', W + 'cr'):
            out.append('\n')
    return ''.join(out)


def run_props(run):
    pr = run.find(W + 'rPr')
    if pr is None:
        return None, False, False, False
    def on(name):
        el = pr.find(W + name)
        return el is not None and el.get(W + 'val') not in ('0', 'false')
    col = pr.find(W + 'color')
    return (col.get(W + 'val').lower() if col is not None and col.get(W + 'val') else None,
            on('b'), on('i'), on('strike'))


def para_text(p, inline=False):
    """Render one <w:p> to Markdown text plus its dominant annotation colour."""
    parts = []
    weight = {}
    for run in p.findall(W + 'r'):
        txt = run_text(run)
        if not txt:
            continue
        col, bold, ital, strike = run_props(run)
        if col in COLOUR_LABEL:
            weight[col] = weight.get(col, 0) + len(txt.strip())
        core = txt.strip()
        if core:
            lead = txt[:len(txt) - len(txt.lstrip())]
            trail = txt[len(txt.rstrip()):]
            if strike:
                core = f'~~{core}~~'
            if bold:
                core = f'**{core}**'
            if ital:
                core = f'*{core}*'
            txt = lead + core + trail
        parts.append(txt)
    text = re.sub(r'\s+', ' ', ''.join(parts)).strip()
    dominant = max(weight, key=weight.get) if weight else None
    if inline:
        return esc(text), dominant
    return text, dominant


def style_of(p):
    pr = p.find(W + 'pPr')
    if pr is None:
        return None
    st = pr.find(W + 'pStyle')
    return st.get(W + 'val') if st is not None else None


def annotate(text, colour):
    """Attach the legend meaning that plain Markdown would otherwise lose."""
    if not colour or not text:
        return text
    label = COLOUR_LABEL[colour]
    # 📞 / 💬 already say it in the text itself; don't double up.
    if text.startswith(('📞', '💬')):
        return text
    return f'{text} `[{label}]`'


def cell_fill(tc):
    pr = tc.find(W + 'tcPr')
    if pr is None:
        return None
    shd = pr.find(W + 'shd')
    return (shd.get(W + 'fill') or '').lower() if shd is not None else None


def cell_lines(tc):
    lines = []
    for p in tc.findall(W + 'p'):
        t, col = para_text(p, inline=True)
        if t:
            lines.append(annotate(t, col))
    return lines


def gridspan(tc):
    pr = tc.find(W + 'tcPr')
    if pr is None:
        return 1
    gs = pr.find(W + 'gridSpan')
    try:
        return int(gs.get(W + 'val')) if gs is not None else 1
    except (TypeError, ValueError):
        return 1


def emit_callout(tc, out):
    """A boxed note — render as a blockquote, never as tabular data."""
    kind = FILL_CALLOUT.get(cell_fill(tc))
    body = cell_lines(tc)
    if not body:
        return
    if kind:
        out.append(f'> **{kind[0]}** *({kind[1]})*')
        out.append('>')
    for ln in body:
        out.append('> ' + re.sub(r'^[•·]\s*', '- ', ln))
    out.append('')


def render_table(tbl, out):
    rows = tbl.findall(W + 'tr')
    if not rows:
        return
    grid = [r.findall(W + 'tc') for r in rows]
    width = max(sum(gridspan(c) for c in r) for r in grid)

    def row_cells(tcs):
        vals = []
        for tc in tcs:
            vals.append(' <br> '.join(cell_lines(tc)) or ' ')
            for _ in range(gridspan(tc) - 1):
                vals.append(' ')
        vals += [' '] * (width - len(vals))
        return vals[:width]

    def is_callout_row(tcs):
        # A lone cell in a multi-column table is a full-width merged note box,
        # whether or not Word gave it a background fill.
        return len(tcs) == 1 and width > 1

    # Split the table on full-width callout rows so boxed notes come out as
    # blockquotes at the position they occur, not as ragged one-cell rows.
    segments, current = [], []
    for r in grid:
        if is_callout_row(r):
            segments.append(('table', current))
            segments.append(('callout', r[0]))
            current = []
        else:
            current.append(r)
    segments.append(('table', current))

    for kind, payload in segments:
        if kind == 'callout':
            emit_callout(payload, out)
            continue
        if not payload:
            continue
        if len(payload) == 1 and len(payload[0]) == 1:
            emit_callout(payload[0][0], out)
            continue
        has_header = any(cell_fill(c) == HEADER_FILL for c in payload[0])
        body_rows = payload[1:] if has_header else payload
        header = row_cells(payload[0]) if has_header else [' '] * width
        out.append('| ' + ' | '.join(header) + ' |')
        out.append('|' + '---|' * width)
        for r in body_rows:
            out.append('| ' + ' | '.join(row_cells(r)) + ' |')
        out.append('')


def convert(src, dst):
    z = zipfile.ZipFile(src)
    root = ET.fromstring(z.read('word/document.xml'))
    body = root.find(W + 'body')
    out = []
    for el in body:
        if el.tag == W + 'p':
            text, col = para_text(el)
            if not text:
                continue
            text = annotate(text, col)
            st = style_of(el)
            if st in ('Heading1', 'Heading2', 'Heading3'):
                # Word styles the whole heading bold; the '#' already carries that.
                bare = re.sub(r'^[*~]+|[*~]+$', '', text).strip()
                hashes = '#' * int(st[-1])
                out += ['', f'{hashes} {bare}', '']
            elif re.match(r'^[•·]\s*', text):
                out.append(re.sub(r'^[•·]\s*', '- ', text))
            else:
                # A paragraph directly after a bullet needs a blank line, or
                # Markdown swallows it into the preceding list item.
                if out and out[-1].startswith('- '):
                    out.append('')
                out += [text, '']
        elif el.tag == W + 'tbl':
            render_table(el, out)

    md = '\n'.join(out)
    md = re.sub(r'\n{3,}', '\n\n', md).strip() + '\n'
    with open(dst, 'w') as f:
        f.write(md)
    print(f'wrote {dst} ({len(md)} bytes, {md.count(chr(10))} lines)')


if __name__ == '__main__':
    convert(sys.argv[1], sys.argv[2])
