#!/usr/bin/env python3
"""Compare two results.json files, keyed on (regulation, article).

Gates (plan section 09 step 2):
  1  chunk_id sets at top-k exactly equal              -- hard failure
  2  chunk_id order differences reported, but every out-of-order pair must
     have a score delta below ORDER_TOL                -- failure above it
  3  max |delta score| below SCORE_TOL
  4  best_similarity within SCORE_TOL and sign(best - gap_floor) unchanged
  5  chunks.json byte-identical                        -- checked by the caller
"""
import json
import sys

SCORE_TOL = 1e-3
ORDER_TOL = 5e-4
GAP_FLOOR = 0.25


def load(path):
    with open(path, encoding="utf-8") as handle:
        doc = json.load(handle)
    return {(r["regulation"], r["article"]): r for r in doc["results"]}, doc


def main(base_path, new_path):
    base, base_doc = load(base_path)
    new, new_doc = load(new_path)
    failures, notes = [], []

    if set(base) != set(new):
        failures.append(f"article sets differ: only-base={sorted(set(base) - set(new))} "
                        f"only-new={sorted(set(new) - set(base))}")
        return report(failures, notes)

    max_delta = 0.0
    max_best_delta = 0.0
    order_diffs = 0
    for key in sorted(base):
        b, n = base[key], new[key]
        b_ids = [r["chunk_id"] for r in b["retrieved"]]
        n_ids = [r["chunk_id"] for r in n["retrieved"]]

        # gate 1 -- set equality
        if set(b_ids) != set(n_ids):
            failures.append(f"{key}: retrieved set differs\n"
                            f"    only-base={sorted(set(b_ids) - set(n_ids))}\n"
                            f"    only-new ={sorted(set(n_ids) - set(b_ids))}")
            continue

        # gate 3 -- per-chunk score delta
        b_scores = {r["chunk_id"]: r["score"] for r in b["retrieved"]}
        n_scores = {r["chunk_id"]: r["score"] for r in n["retrieved"]}
        for cid in b_ids:
            delta = abs(b_scores[cid] - n_scores[cid])
            max_delta = max(max_delta, delta)
            if delta > SCORE_TOL:
                failures.append(f"{key}: {cid} score {b_scores[cid]} -> "
                                f"{n_scores[cid]} (delta {delta:.6f})")

        # gate 2 -- order, tolerated only among near-ties
        if b_ids != n_ids:
            order_diffs += 1
            b_rank = {cid: i for i, cid in enumerate(b_ids)}
            benign = True
            for i, cid in enumerate(n_ids):
                for other in n_ids[i + 1:]:
                    if b_rank[cid] > b_rank[other]:      # this pair swapped
                        gap = abs(b_scores[cid] - b_scores[other])
                        if gap > ORDER_TOL:
                            failures.append(
                                f"{key}: non-benign reorder {other} <-> {cid}, "
                                f"baseline scores {b_scores[other]} / {b_scores[cid]} "
                                f"(gap {gap:.6f} > {ORDER_TOL})")
                            benign = False
            if benign:
                notes.append(f"{key}: benign reorder {b_ids} -> {n_ids}")

        # gate 4 -- best_similarity and the auto-gap decision
        bb, nb = b["best_similarity"], n["best_similarity"]
        max_best_delta = max(max_best_delta, abs(bb - nb))
        if abs(bb - nb) > SCORE_TOL:
            failures.append(f"{key}: best_similarity {bb} -> {nb}")
        if (bb >= GAP_FLOOR) != (nb >= GAP_FLOOR):
            failures.append(f"{key}: auto-gap decision flips at floor {GAP_FLOOR} "
                            f"({bb} -> {nb})")

    notes.append(f"articles compared      {len(base)}")
    notes.append(f"max |delta score|      {max_delta:.2e}  (tol {SCORE_TOL:.0e})")
    notes.append(f"max |delta best_sim|   {max_best_delta:.2e}  (tol {SCORE_TOL:.0e})")
    notes.append(f"articles reordered     {order_diffs}")
    return report(failures, notes)


def report(failures, notes):
    for note in notes:
        print(f"  {note}")
    if failures:
        print(f"\nFAIL -- {len(failures)} problem(s):")
        for failure in failures:
            print(f"  ! {failure}")
        return 1
    print("\nPASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
