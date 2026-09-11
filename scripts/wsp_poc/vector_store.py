#!/usr/bin/env python3
"""Qdrant-backed vector store for the WSP validation POC.

Everything Qdrant-specific lives here and nowhere else -- the same spirit as the
provider seam in validate_wsp.py, where everything OpenAI-specific is confined to
OpenAIEmbedding / OpenAIJudge. Porting to OpenSearch or pgvector is a rewrite of
this module and nothing else.

Two collections, deliberately different in shape:

    <prefix>_chunks_<model>     the searchable WSP chunk index. COSINE, because
                                Qdrant L2-normalises on write and returns the dot
                                product of unit vectors -- exactly what the old
                                numpy path computed.

    <prefix>_embcache_<model>   the embedding memo cache, replacing
                                out/regs/embeddings.json.gz. DOT, never COSINE:
                                under Cosine distance Qdrant normalises the stored
                                vector and does not keep the original, so
                                retrieve(with_vectors=True) would hand back a
                                normalised vector rather than the one the provider
                                returned. This collection is a key/value store and
                                is never searched, so DOT keeps it lossless.

Neither collection ever builds an HNSW graph (indexing_threshold=0) and every
search passes exact=True. At 200-500 points a full scan is both faster than ANN
and exact, which removes recall from the list of things a parity check has to
reason about.
"""
import hashlib
import re
import sys
import time
import uuid
from datetime import datetime, timezone

from qdrant_client import QdrantClient, models

# Namespace for every point id this module derives. Changing it orphans every
# stored point in every deployment -- so never change it.
POINT_NS = uuid.UUID("1f0c7d3a-6b21-4a9e-9f5b-2e6f4c8a17d3")

# Bumped when WspChunker.embed_text changes what text goes to the embedder. It is
# payload metadata, not part of the point id: the explicit lever for "the embedded
# text recipe changed, this index is stale".
EMBED_TEXT_VERSION = "wsp-embed-1"

# Above this many points the client-side max-merge stops fetching every chunk per
# unit and falls back to an over-fetch approximation. See QdrantRetriever.rank.
EXHAUSTIVE_FETCH_LIMIT = 2000
OVERFETCH_FACTOR = 10


def cache_key(model, text):
    """Byte-identical to the old EmbeddingCache.key -- sha256(model \\x00 text).

    Kept identical so the existing embeddings.json.gz can be backfilled into
    Qdrant without re-embedding a single unit.
    """
    return hashlib.sha256(f"{model}\x00{text}".encode("utf-8")).hexdigest()


def point_id(kind, value):
    """Deterministic UUIDv5 point id. Qdrant accepts uint64 or UUID only.

    A UUID rather than int(sha256_hex[:16], 16): the int form halves the collision
    space to 64 bits and mixes id *types* across collections, which invites a bug
    where a str is passed where an int is expected -- retrieve() then returns zero
    records instead of raising.
    """
    return str(uuid.uuid5(POINT_NS, f"{kind}\x00{value}"))


def slug(text):
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


class QdrantVectorStore:
    """Connection, collection naming and lifecycle. Holds no run state."""

    def __init__(self, url, prefix, model, dim, store_chunk_text=True,
                 timeout=30, client=None):
        self.url = url
        self.prefix = prefix
        self.model = model
        self.dim = dim
        self.store_chunk_text = store_chunk_text
        # `local:<dir>` selects qdrant-client's embedded local mode, which needs no
        # server. It exists for CI and for a parity check on a machine with no
        # Docker daemon -- it is NOT the deployment target: it is single-process,
        # ignores payload indexes, and always searches exhaustively.
        if client is not None:
            self.client = client
        elif str(url).startswith("local:"):
            self.client = QdrantClient(path=url.split(":", 1)[1])
        else:
            self.client = QdrantClient(url=url, timeout=timeout)
        self._owns_client = client is None
        self.chunk_collection = f"{prefix}_chunks_{slug(model)}"
        self.cache_collection = f"{prefix}_embcache_{slug(model)}"

    def wait_ready(self, timeout=30, interval=0.5):
        """Poll until the server answers, so `docker compose up -d qdrant` and a
        run issued straight after it do not race.

        Deliberately here rather than in a compose healthcheck: the qdrant image
        ships no curl or wget, and this also covers the "Qdrant in compose, script
        run natively" workflow that a compose healthcheck cannot.
        """
        deadline = time.time() + timeout
        last = None
        while time.time() < deadline:
            try:
                self.client.get_collections()
                return True
            except Exception as exc:                # transport errors vary by version
                last = exc
                time.sleep(interval)
        raise SystemExit(
            f"qdrant not reachable at {self.url} after {timeout}s ({last}).\n"
            f"  docker compose up -d qdrant\n"
            f"or point --qdrant-url / QDRANT_URL at a running server.")

    def _exists(self, name):
        return self.client.collection_exists(collection_name=name)

    def ensure_collections(self, recreate_index=False, reset_cache=False):
        if recreate_index and self._exists(self.chunk_collection):
            self._warn_foreign_docs()
            self.client.delete_collection(collection_name=self.chunk_collection)
        if reset_cache and self._exists(self.cache_collection):
            self.client.delete_collection(collection_name=self.cache_collection)

        if not self._exists(self.chunk_collection):
            self.client.create_collection(
                collection_name=self.chunk_collection,
                vectors_config=models.VectorParams(
                    size=self.dim, distance=models.Distance.COSINE),
                # 200-500 points. Never build an HNSW graph: a full scan is both
                # faster and exact, and it removes ANN recall as a variable.
                optimizers_config=models.OptimizersConfigDiff(indexing_threshold=0),
            )
            for field in ("doc", "chunk_id"):
                self.client.create_payload_index(
                    collection_name=self.chunk_collection, field_name=field,
                    field_schema=models.PayloadSchemaType.KEYWORD)

        if not self._exists(self.cache_collection):
            self.client.create_collection(
                collection_name=self.cache_collection,
                vectors_config=models.VectorParams(
                    size=self.dim, distance=models.Distance.DOT, on_disk=True),
                hnsw_config=models.HnswConfigDiff(m=0),
                optimizers_config=models.OptimizersConfigDiff(indexing_threshold=0),
            )

    def _warn_foreign_docs(self):
        """--recreate-index drops the whole chunk collection, which may hold docs
        that are not part of this run. Say so rather than silently deleting."""
        try:
            total = self.client.count(collection_name=self.chunk_collection,
                                      exact=True).count
        except Exception:
            return
        if total:
            print(f"  ! --recreate-index drops {total} existing chunk point(s) in "
                  f"{self.chunk_collection}, including any belonging to documents "
                  f"outside this run (re-index them to restore)", file=sys.stderr)

    def describe(self):
        """Provenance for results.json -- which index produced these numbers."""
        return {
            "backend": "qdrant",
            "url": self.url,
            "chunk_collection": self.chunk_collection,
            "cache_collection": self.cache_collection,
            "exact_search": True,
            "embed_text_version": EMBED_TEXT_VERSION,
        }

    def close(self):
        if self._owns_client:
            self.client.close()


class QdrantEmbeddingCache:
    """Read-through memo cache, replacing the gzipped-JSON EmbeddingCache.

    A naive port makes get() a network call -- roughly 1500 round trips per run.
    prefetch() batches the lookups into a handful of retrieve() calls and get() is
    then memory-only by contract; callers must prefetch before they get.
    """

    def __init__(self, store, batch=512):
        self.store = store
        self.batch = batch
        self.mem = {}
        self.pending = {}
        self.written = 0

    def key(self, model, text):
        return cache_key(model, text)

    def prefetch(self, model, texts):
        """One batched round trip per `batch` unknown keys. Returns (hit, miss)."""
        wanted = {}
        for text in texts:
            key = self.key(model, text)
            if key not in self.mem:
                wanted[point_id("embcache", key)] = key
        ids = list(wanted)
        for start in range(0, len(ids), self.batch):
            records = self.store.client.retrieve(
                collection_name=self.store.cache_collection,
                ids=ids[start:start + self.batch],
                with_payload=False, with_vectors=True)
            for record in records:              # absent ids are simply omitted
                self.mem[wanted[str(record.id)]] = list(record.vector)
        hits = sum(1 for t in texts if self.key(model, t) in self.mem)
        return hits, len(texts) - hits

    def get(self, model, text):
        return self.mem.get(self.key(model, text))

    def put(self, model, text, vector):
        # 6dp rounding is unchanged from the gz cache: cosine-neutral, and it is
        # what makes a backfilled Qdrant cache byte-comparable with the old one.
        rounded = [round(v, 6) for v in vector]
        key = self.key(model, text)
        self.mem[key] = rounded
        self.pending[key] = rounded

    def save(self):
        """Flush buffered puts. Called where the old cache wrote its .gz, so a
        crash mid-run keeps whatever has already been embedded. Returns the
        cumulative count, not this flush's, since it is called per batch."""
        if not self.pending:
            return self.written
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        points = [
            models.PointStruct(
                id=point_id("embcache", key), vector=vector,
                # No text, matching the old cache's property that the memo store
                # carries no client WSP prose.
                payload={"key": key, "model": self.store.model,
                         "dim": len(vector), "created_at": now})
            for key, vector in self.pending.items()
        ]
        written = len(points)
        for start in range(0, written, self.batch):
            self.store.client.upsert(collection_name=self.store.cache_collection,
                                     points=points[start:start + self.batch],
                                     wait=True)
        self.pending.clear()
        self.written += written
        return self.written


class QdrantRetriever:
    """Cosine ranking of WSP chunks against article units, scored max-over-units.

    Same contract as NumpyRetriever.rank: best score per chunk across an article's
    units, top-k descending. The max-merge happens client-side over a batched
    query, which is mathematically identical to (matrix @ units.T).max(axis=1) as
    long as every chunk is fetched for every unit.
    """

    def __init__(self, store, chunks, gap_floor=0.25, top_k=6):
        self.store = store
        self.chunks = chunks
        self.gap_floor = gap_floor
        self.top_k = top_k
        self.docs = sorted({c.doc for c in chunks})
        self.by_pid = {point_id("chunk", c.chunk_id): c for c in chunks}
        self.filter = models.Filter(must=[models.FieldCondition(
            key="doc", match=models.MatchAny(any=self.docs))])
        self.limit = len(chunks)
        if len(chunks) > EXHAUSTIVE_FETCH_LIMIT:
            # Over-fetching approximates the max-merge: a chunk whose max sits at
            # rank 40 for one unit is dropped by a limit of 60 even when that max
            # is the global best. Never silent.
            self.limit = min(len(chunks), self.top_k * OVERFETCH_FACTOR)
            print(f"  ! {len(chunks)} chunks exceeds {EXHAUSTIVE_FETCH_LIMIT}; "
                  f"falling back to over-fetch limit {self.limit}, which makes the "
                  f"max-over-units merge approximate", file=sys.stderr)

    def index(self, chunk_vectors):
        """Upsert this run's points, sweep orphans, then verify the doc filter."""
        points = []
        for chunk, vector in zip(self.chunks, chunk_vectors):
            payload = {
                "chunk_id": chunk.chunk_id,
                "doc": chunk.doc,
                "content_hash": chunk.content_hash,
                "heading": chunk.heading,
                "heading_path": list(chunk.heading_path),
                "page_start": chunk.page_start,
                "page_end": chunk.page_end,
                "tokens": chunk.tokens,
                "embedding_model": self.store.model,
                "embed_text_version": EMBED_TEXT_VERSION,
            }
            if self.store.store_chunk_text:
                payload["text"] = chunk.text
            points.append(models.PointStruct(
                id=point_id("chunk", chunk.chunk_id), vector=list(vector),
                payload=payload))

        for start in range(0, len(points), 256):
            self.store.client.upsert(collection_name=self.store.chunk_collection,
                                     points=points[start:start + 256], wait=True)

        # Sweep: anything under this run's docs that this run did not write is a
        # leftover from a previous extraction. Re-running an unchanged manual
        # converges; a re-extraction with fewer chunks drops the tail; a crash
        # mid-run leaves a superset, never an empty index.
        self.store.client.delete(
            collection_name=self.store.chunk_collection, wait=True,
            points_selector=models.FilterSelector(filter=models.Filter(
                must=[models.FieldCondition(key="doc",
                                            match=models.MatchAny(any=self.docs))],
                must_not=[models.HasIdCondition(has_id=[p.id for p in points])])))

        # Guard: a doc-name typo or a stale filter would silently return zero hits
        # for every article and auto-gap the entire run with a plausible report.
        visible = self.store.client.count(collection_name=self.store.chunk_collection,
                                          count_filter=self.filter, exact=True).count
        if visible != len(points):
            raise SystemExit(f"index guard: {visible} points visible through the doc "
                             f"filter {self.docs}, expected {len(points)}")
        return len(points)

    def rank(self, unit_vectors):
        requests = [models.QueryRequest(
                        query=list(vector), limit=self.limit, filter=self.filter,
                        params=models.SearchParams(exact=True),
                        # QueryRequest says with_vector (singular); client.retrieve
                        # and client.query_points say with_vectors (plural).
                        with_payload=False, with_vector=False)
                    for vector in unit_vectors]
        responses = self.store.client.query_batch_points(
            collection_name=self.store.chunk_collection, requests=requests)
        best = {}
        for response in responses:              # list[QueryResponse]; hits at .points
            for hit in response.points:
                pid = str(hit.id)
                if hit.score > best.get(pid, -2.0):
                    best[pid] = hit.score
        # np.argsort defaults to an unstable quicksort, so the old order among
        # equal scores was arbitrary and Qdrant's is unspecified. chunk_id as the
        # secondary key makes this deterministic at no cost.
        order = sorted(best.items(),
                       key=lambda kv: (-kv[1], self.by_pid[kv[0]].chunk_id))
        return [(self.by_pid[pid], float(score)) for pid, score in order[:self.top_k]]
