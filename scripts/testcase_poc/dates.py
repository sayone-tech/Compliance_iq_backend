"""Deterministic date arithmetic for the judge.

Mini-tier models get "is January 5, 2023 within 12 months of 2026-09-11?" wrong
often enough to flip a verdict, so the dates in a step's excerpts are found and
compared here, in code, and handed to the model as facts. The model still
decides what each date *means*; it just no longer has to do the arithmetic.
"""
import re
from calendar import monthrange
from datetime import date

MONTHS = {m: i for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july", "august",
     "september", "october", "november", "december"], start=1)}
MONTHS.update({m[:3]: i for m, i in list(MONTHS.items())})

_MONTH_RE = r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*"
# "January 5th, 2023" / "January 5 , 2023" (pdftotext splits the superscript) / "5 January 2023"
LONG_RE = re.compile(
    rf"\b({_MONTH_RE})\.?\s+(\d{{1,2}})(?:\s*(?:st|nd|rd|th))?\s*,?\s+(\d{{4}})\b|"
    rf"\b(\d{{1,2}})(?:st|nd|rd|th)?\s+({_MONTH_RE})\.?\s*,?\s+(\d{{4}})\b", re.IGNORECASE)
NUMERIC_RE = re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b|\b(\d{4})-(\d{2})-(\d{2})\b")


def months_before(d, months):
    year, month = d.year, d.month - months
    while month <= 0:
        year, month = year - 1, month + 12
    return date(year, month, min(d.day, monthrange(year, month)[1]))


def _safe_date(year, month, day):
    try:
        return date(year, month, day)
    except ValueError:
        return None


def find_dates(text):
    """Return [(surface_text, date)] in order of appearance, de-duplicated."""
    found, seen = [], set()
    for m in LONG_RE.finditer(text):
        if m.group(1):
            mon, day, year = m.group(1), m.group(2), m.group(3)
        else:
            day, mon, year = m.group(4), m.group(5), m.group(6)
        month = MONTHS.get(mon.lower()[:3])
        d = _safe_date(int(year), month, int(day)) if month else None
        if d and d not in seen:
            seen.add(d)
            found.append((re.sub(r"\s+", " ", m.group(0)), d))
    for m in NUMERIC_RE.finditer(text):
        if m.group(1):
            d = _safe_date(int(m.group(3)), int(m.group(1)), int(m.group(2)))
        else:
            d = _safe_date(int(m.group(4)), int(m.group(5)), int(m.group(6)))
        if d and d not in seen:
            seen.add(d)
            found.append((m.group(0), d))
    return found


def date_facts(text, as_of, cutoff_months=12, limit=25):
    """Lines the judge can rely on, e.g.
    'January 5 , 2023 = 2023-01-05: 3 years 8 months before 2026-09-11 -> OLDER than the 12-month cutoff (2025-09-11)'"""
    as_of = date.fromisoformat(as_of) if isinstance(as_of, str) else as_of
    cutoff = months_before(as_of, cutoff_months)
    lines = []
    for surface, d in find_dates(text)[:limit]:
        if d > as_of:
            rel = "in the FUTURE relative to the date of testing"
        else:
            total = (as_of.year - d.year) * 12 + (as_of.month - d.month) - (as_of.day < d.day)
            years, months = divmod(max(total, 0), 12)
            age = ", ".join(p for p in [f"{years} year{'s' if years != 1 else ''}" if years else "",
                                        f"{months} month{'s' if months != 1 else ''}" if months or not years else ""] if p)
            status = ("OLDER than" if d < cutoff else "within") + f" the {cutoff_months}-month cutoff ({cutoff.isoformat()})"
            rel = f"{age} before {as_of.isoformat()} -> {status}"
        lines.append(f"- \"{surface}\" = {d.isoformat()}: {rel}")
    return "\n".join(lines)
