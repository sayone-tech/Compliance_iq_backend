#!/usr/bin/env python3
"""Smoke test for vector_store.py -- confirms the two API asymmetries and the
DOT-versus-COSINE storage behaviour empirically rather than from the docs.

  python3 scripts/wsp_poc/tools/smoke_vector_store.py                      # local mode
  python3 scripts/wsp_poc/tools/smoke_vector_store.py http://127.0.0.1:6333  # a server
"""
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))           # scripts/wsp_poc

from qdrant_client import QdrantClient                       # noqa: E402
from vector_store import (QdrantEmbeddingCache, QdrantVectorStore,  # noqa: E402
                          cache_key, point_id)

DIM = 8


class FakeChunk:
    def __init__(self, cid, doc, vec):
        self.chunk_id = cid
        self.doc = doc
        self.heading_path = ["A", "B"]
        self.heading = "B"
        self.page_start = 1
        self.page_end = 2
        self.tokens = 10
        self.text = f"body of {cid}"
        self.content_hash = "deadbeef"
        self.vector = vec


def main(url=None):
    failures = []
    if url:
        store = QdrantVectorStore(url=url, prefix="smoke", model="text-embedding-3-small",
                                  dim=DIM)
        store.wait_ready(timeout=15)
    else:
        tmp = tempfile.mkdtemp(prefix="qdrant-local-")
        store = QdrantVectorStore(url=f"local:{tmp}", prefix="smoke",
                                  model="text-embedding-3-small", dim=DIM,
                                  client=QdrantClient(path=tmp))
    print(f"collections: {store.chunk_collection} / {store.cache_collection}")
    for name in (store.chunk_collection, store.cache_collection):
        if store.client.collection_exists(collection_name=name):
            store.client.delete_collection(collection_name=name)
    store.ensure_collections()

    # ---- 1. cache_key must equal the old EmbeddingCache.key -------------------
    import hashlib
    old = hashlib.sha256("text-embedding-3-small\x00hello".encode("utf-8")).hexdigest()
    if cache_key("text-embedding-3-small", "hello") != old:
        failures.append("cache_key differs from the old EmbeddingCache.key")
    print(f"cache_key            {cache_key('text-embedding-3-small', 'hello')[:16]}...  ok")

    # ---- 2. DOT storage is lossless; a raw vector round-trips unchanged -------
    cache = QdrantEmbeddingCache(store)
    raw = [3.0, 4.0] + [0.0] * (DIM - 2)                # norm 5, obviously not unit
    cache.put("text-embedding-3-small", "hello", raw)
    cache.save()
    cache2 = QdrantEmbeddingCache(store)
    hits, misses = cache2.prefetch("text-embedding-3-small", ["hello", "absent"])
    got = cache2.get("text-embedding-3-small", "hello")
    print(f"cache prefetch       {hits} hit / {misses} miss")
    if (hits, misses) != (1, 1):
        failures.append(f"prefetch returned {hits}/{misses}, expected 1 hit / 1 miss")
    if got is None:
        failures.append("cache round trip returned nothing")
    elif max(abs(a - b) for a, b in zip(got, raw)) > 1e-6:
        failures.append(f"DOT collection did not store the vector losslessly: "
                        f"{got[:2]} != {raw[:2]} -- Qdrant normalised it")
    else:
        print(f"cache round trip     {got[:2]} == {raw[:2]}  (lossless, DOT ok)")
    if cache2.get("text-embedding-3-small", "absent") is not None:
        failures.append("get() invented a value for an absent key")

    # ---- 3. chunk index: upsert, sweep, count guard, batched query ------------
    from vector_store import QdrantRetriever
    chunks = [FakeChunk("d1:c1", "d1", [1.0] + [0.0] * (DIM - 1)),
              FakeChunk("d1:c2", "d1", [0.0, 1.0] + [0.0] * (DIM - 2)),
              FakeChunk("d2:c1", "d2", [0.0, 0.0, 1.0] + [0.0] * (DIM - 3))]
    retr = QdrantRetriever(store, chunks, top_k=2)
    n = retr.index([c.vector for c in chunks])
    print(f"indexed              {n} points, guard passed")

    # query with two units: max-over-units must pick c1 for unit A, c2 for unit B
    units = [[2.0] + [0.0] * (DIM - 1), [0.0, 5.0] + [0.0] * (DIM - 2)]
    ranked = retr.rank(units)
    ids = [c.chunk_id for c, _ in ranked]
    print(f"rank(2 units)        {[(c.chunk_id, round(s, 4)) for c, s in ranked]}")
    if set(ids) != {"d1:c1", "d1:c2"}:
        failures.append(f"rank returned {ids}, expected the two d1 chunks "
                        f"(d2 must be excluded by the doc filter)")
    if ranked and abs(ranked[0][1] - 1.0) > 1e-5:
        failures.append(f"top score {ranked[0][1]} != 1.0 -- COSINE is not "
                        f"returning unit-vector dot products")

    # sweep: re-index d1 with one chunk only; the orphan must go
    survivor = [chunks[0]]
    retr2 = QdrantRetriever(store, survivor, top_k=2)
    retr2.index([c.vector for c in survivor])
    left = [c.chunk_id for c, _ in retr2.rank(units)]
    print(f"after orphan sweep   {left}")
    if left != ["d1:c1"]:
        failures.append(f"orphan sweep left {left}, expected ['d1:c1']")

    # d2 untouched by a d1-scoped run
    retr3 = QdrantRetriever(store, [chunks[2]], top_k=2)
    d2_visible = store.client.count(collection_name=store.chunk_collection,
                                    count_filter=retr3.filter, exact=True).count
    print(f"d2 points intact     {d2_visible}")
    if d2_visible != 1:
        failures.append(f"a d1-scoped run changed d2: {d2_visible} points, expected 1")

    # ---- 4. point ids are UUIDs, stable, and namespaced by kind --------------
    if point_id("chunk", "x") == point_id("embcache", "x"):
        failures.append("point_id is not namespaced by kind")
    print(f"point_id             {point_id('chunk', 'd1:c1')}")

    store.close()
    if failures:
        print(f"\nFAIL -- {len(failures)}:")
        for f in failures:
            print(f"  ! {f}")
        return 1
    print("\nPASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else None))
