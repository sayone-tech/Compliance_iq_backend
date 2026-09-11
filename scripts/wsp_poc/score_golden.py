#!/usr/bin/env python3
"""Score a validate_wsp.py run against the golden set.

The two AI stages are scored separately, on purpose:

  retrieval  recall@k -- for each golden item that has an evidence hint, did a
             chunk containing that hint reach the top k for the article?
  judgment   verdict accuracy, reported both over all items and over only those
             items where retrieval succeeded (judgment given correct retrieval).

A blended accuracy number cannot tell you which seam to fix -- chunking and
embedding, or the prompt and rubric. This split is the seed of the Section 6.2
"verification text vectors" methodology and the proposed measurement method for
the 85% UAT accuracy bar (EV-01 / EV-08).

Usage, from the repository root:

    python3 scripts/wsp_poc/score_golden.py \
        --results out/report/sample_wsp/results.json \
        --chunks  out/report/sample_wsp/chunks.json \
        --run sample_wsp
"""
import argparse
import json
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
GOLDEN = os.path.join(HERE, "golden_set.json")

VERDICTS = ["covered", "partial", "gap"]


def normalise(verdict):
    """The report downgrades a DORA Art. 45-style gap to 'not applicable
    (voluntary)'. For scoring that is still a gap."""
    return "gap" if verdict.startswith("not applicable") else verdict


def hit(item, result, chunks_by_id):
    """Did a chunk matching any evidence hint reach the retrieved set?"""
    hints = [h.lower() for h in item.get("evidence_hint") or []]
    if not hints:
        return None                      # gap items have no relevant chunk to find
    for entry in result["retrieved"]:
        chunk = chunks_by_id.get(entry["chunk_id"])
        haystack = ((chunk["text"] if chunk else "")
                    + " " + entry["heading"]).lower()
        if any(h in haystack for h in hints):
            return True
    return False


def main():
    parser = argparse.ArgumentParser(description="Score a run against the golden set.")
    parser.add_argument("--results", required=True, help="results.json from validate_wsp.py")
    parser.add_argument("--chunks", required=True, help="chunks.json from validate_wsp.py")
    parser.add_argument("--run", required=True, help="golden-set run key (e.g. sample_wsp)")
    parser.add_argument("--golden", default=GOLDEN)
    parser.add_argument("--json", metavar="PATH", help="also write the scores as JSON")
    args = parser.parse_args()

    with open(args.golden, encoding="utf-8") as handle:
        golden = json.load(handle)
    if args.run not in golden["runs"]:
        raise SystemExit(f"unknown run '{args.run}'; known: {', '.join(golden['runs'])}")
    items = golden["runs"][args.run]["items"]

    with open(args.results, encoding="utf-8") as handle:
        payload = json.load(handle)
    results = {(r["regulation"], r["article_number"]): r for r in payload["results"]}
    with open(args.chunks, encoding="utf-8") as handle:
        chunks_by_id = {c["chunk_id"]: c for c in json.load(handle)}

    rows, retrieval = [], {"scored": 0, "hits": 0}
    confusion = defaultdict(int)
    unverified = 0
    for item in items:
        key = (item["regulation"], item["article"])
        result = results.get(key)
        if result is None:
            print(f"  ! {item['id']}: {key[0]} Art. {key[1]} is not in the results "
                  f"(out of scope for this profile?)", file=sys.stderr)
            continue
        if not item.get("verified"):
            unverified += 1
        got = normalise(result["effective_verdict"] if "effective_verdict" in result
                        else result["verdict"])
        expected = item["expected_verdict"]
        recall = hit(item, result, chunks_by_id)
        if recall is not None:
            retrieval["scored"] += 1
            retrieval["hits"] += int(recall)
        confusion[(expected, got)] += 1
        rows.append({
            "id": item["id"], "regulation": key[0], "article": key[1],
            "expected": expected, "got": got, "correct": expected == got,
            "retrieval_hit": recall, "auto_gap": result["auto_gap"],
            "best_similarity": result["best_similarity"],
            "verified_label": bool(item.get("verified")),
        })

    total = len(rows)
    correct = sum(1 for r in rows if r["correct"])
    given_retrieval = [r for r in rows if r["retrieval_hit"] is True]
    gap_items = [r for r in rows if r["expected"] == "gap"]

    print(f"\nrun: {args.run}   items scored: {total}")
    if unverified:
        print(f"  ! {unverified} label(s) still marked verified=false -- confirm them "
              f"against the manual before quoting these numbers")

    print(f"\nretrieval (recall@{payload['context']['top_k']})")
    if retrieval["scored"]:
        print(f"  {retrieval['hits']}/{retrieval['scored']} = "
              f"{retrieval['hits'] / retrieval['scored']:.0%}   "
              f"(gap items excluded -- they have no relevant chunk to retrieve)")
    else:
        print("  no items carried an evidence hint")

    print("\njudgment")
    print(f"  overall verdict accuracy            {correct}/{total} = "
          f"{correct / total:.0%}" if total else "  no items")
    if given_retrieval:
        ok = sum(1 for r in given_retrieval if r["correct"])
        print(f"  accuracy given correct retrieval    {ok}/{len(given_retrieval)} = "
              f"{ok / len(given_retrieval):.0%}")
    if gap_items:
        ok = sum(1 for r in gap_items if r["correct"])
        auto = sum(1 for r in gap_items if r["auto_gap"])
        print(f"  gap items correct                   {ok}/{len(gap_items)} = "
              f"{ok / len(gap_items):.0%}   ({auto} resolved by the auto-gap floor, "
              f"no LLM call)")

    print("\nper-verdict precision / recall")
    for verdict in VERDICTS:
        tp = confusion.get((verdict, verdict), 0)
        fp = sum(n for (exp, got), n in confusion.items() if got == verdict and exp != verdict)
        fn = sum(n for (exp, got), n in confusion.items() if exp == verdict and got != verdict)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall_v = tp / (tp + fn) if tp + fn else 0.0
        print(f"  {verdict:<8} precision {precision:.0%}  recall {recall_v:.0%}  "
              f"(tp {tp}, fp {fp}, fn {fn})")

    print("\nconfusion (expected -> got)")
    for expected in VERDICTS:
        got_counts = {g: n for (e, g), n in confusion.items() if e == expected and n}
        if got_counts:
            print(f"  {expected:<8} " + ", ".join(f"{g}:{n}" for g, n in sorted(got_counts.items())))

    misses = [r for r in rows if not r["correct"]]
    if misses:
        print("\nmisses")
        for r in misses:
            print(f"  {r['id']}  {r['regulation']} Art. {r['article']:<3} "
                  f"expected {r['expected']:<8} got {r['got']:<8} "
                  f"retrieval {'hit' if r['retrieval_hit'] else 'miss' if r['retrieval_hit'] is False else 'n/a'}"
                  f"  sim {r['best_similarity']:.3f}")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as handle:
            json.dump({"run": args.run, "rows": rows,
                       "retrieval": retrieval,
                       "verdict_accuracy": correct / total if total else None,
                       "unverified_labels": unverified}, handle, indent=2)
        print(f"\n  wrote {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
