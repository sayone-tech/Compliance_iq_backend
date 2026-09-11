#!/usr/bin/env python3
"""Backfill the old gzipped embedding cache into the Qdrant cache collection.

The migration itself does not need this: re-embedding all 766 vectors costs about
$0.003. It exists for the *parity check*. The keys in embeddings.json.gz are
one-way hashes, but the inputs are not lost -- chunk embed-texts reconstruct from
out/report/*/chunks.json exactly as WspChunker.embed_text builds them, and article
units come from RegulationCorpus.units(). Backfilling means the post-migration run
consumes the identical 6dp vectors the pre-migration run did, so any score
difference is attributable solely to the retrieval layer, which is the one thing
being validated -- and the parity run costs $0.

    python3 scripts/wsp_poc/tools/backfill_embedding_cache.py \\
        --gz out/regs/embeddings.json.gz \\
        --chunks out/report/sample_wsp/chunks.json \\
        --chunks out/report/triad_wsp/chunks.json \\
        --regs-cache out/regs/ --profile exchange,execution,custody

Exits non-zero below --min-hit-rate: a miss means the embed-text recipe changed
since the cache was written, and the parity check would then be meaningless.
"""
import argparse
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
POC = os.path.dirname(HERE)
sys.path.insert(0, POC)
sys.path.insert(0, os.path.dirname(POC))            # scripts/ -- for fetch_regulation

import validate_wsp as wsp                           # noqa: E402
from vector_store import (QdrantEmbeddingCache, QdrantVectorStore,  # noqa: E402
                          cache_key)


def chunk_texts(paths):
    """Reconstruct WspChunker.embed_text for every chunk in every chunks.json."""
    texts = []
    for path in paths:
        with open(path, encoding="utf-8") as handle:
            for record in json.load(handle):
                texts.append(" > ".join(record["heading_path"]) + "\n" + record["text"])
    return texts


def unit_texts(regs_cache, profile, celex_map):
    corpus = wsp.RegulationCorpus(regs_cache, offline=True)
    articles = corpus.load(celex_map, profile)
    return [unit for article in articles for unit in corpus.units(article)]


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--gz", default="out/regs/embeddings.json.gz",
                        help="the old gzipped cache to read")
    parser.add_argument("--chunks", action="append", default=[],
                        help="a chunks.json from a previous report (repeatable)")
    parser.add_argument("--regs-cache", default="out/regs")
    parser.add_argument("--profile", default=",".join(wsp.DEFAULT_PROFILE))
    parser.add_argument("--celex", action="append")
    parser.add_argument("--embedding-model", default="text-embedding-3-small")
    parser.add_argument("--qdrant-url",
                        default=os.environ.get("QDRANT_URL", "http://127.0.0.1:6333"))
    parser.add_argument("--collection-prefix",
                        default=os.environ.get("QDRANT_COLLECTION_PREFIX", "wsp"))
    parser.add_argument("--min-hit-rate", type=float, default=0.95,
                        help="fail below this share of gz keys accounted for")
    parser.add_argument("--dry-run", action="store_true",
                        help="report the hit rate without writing to Qdrant")
    args = parser.parse_args()

    with gzip.open(args.gz, "rt", encoding="utf-8") as handle:
        stored = json.load(handle)
    print(f"{args.gz}: {len(stored)} cached vectors")

    celex_map = dict(wsp.DEFAULT_CELEX)
    for override in args.celex or []:
        name, _, value = override.partition("=")
        if name not in celex_map:
            raise SystemExit(f"--celex expects DORA=... or MiCA=..., got '{override}'")
        celex_map[name] = value
    profile = [p.strip() for p in args.profile.split(",") if p.strip()]

    candidates = {"chunk": chunk_texts(args.chunks),
                  "unit": unit_texts(args.regs_cache, profile, celex_map)}

    matched, found = {}, {"chunk": 0, "unit": 0}
    for kind, texts in candidates.items():
        for text in texts:
            key = cache_key(args.embedding_model, text)
            if key in stored and key not in matched:
                matched[key] = (text, stored[key])
                found[kind] += 1
        print(f"  {kind:<6} {len(texts):>5} candidate texts, {found[kind]:>5} hit")

    rate = len(matched) / len(stored) if stored else 0.0
    print(f"\n{len(matched)}/{len(stored)} keys backfilled ({rate:.1%}), "
          f"{len(stored) - len(matched)} unaccounted for")

    if not args.dry_run and matched:
        dim = wsp.EMBEDDING_DIMS[args.embedding_model]
        store = QdrantVectorStore(url=args.qdrant_url, prefix=args.collection_prefix,
                                  model=args.embedding_model, dim=dim)
        store.wait_ready()
        store.ensure_collections()
        cache = QdrantEmbeddingCache(store)
        for text, vector in matched.values():
            # put() re-rounds to 6dp, which is a no-op on values that were already
            # written at 6dp -- the stored vectors stay bit-for-bit what the old
            # cache held.
            cache.put(args.embedding_model, text, vector)
        written = cache.save()
        total = store.client.count(collection_name=store.cache_collection,
                                   exact=True).count
        print(f"upserted {written} point(s) into {store.cache_collection} "
              f"({total} total)")
        store.close()

    if rate < args.min_hit_rate:
        print(f"\nFAIL: hit rate {rate:.1%} is below {args.min_hit_rate:.0%}. The "
              f"embed-text recipe has probably changed since the cache was written; "
              f"a parity check against it would be meaningless.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
