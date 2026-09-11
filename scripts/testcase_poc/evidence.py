"""Evidence ingestion and retrieval, built on the WSP POC pieces.

    PDF --build_document--> text with [[page:N]] --WspChunker--> chunks
        --OpenAIEmbedding (memo-cached in Qdrant)--> vectors --QdrantRetriever.index-->

Indexes are kept in-process by document hash so the seven parallel judge_step
nodes share one, and a repeat run of the same PDF costs no embedding tokens
(the memo cache) and no re-extraction (this module's cache).
"""
import hashlib
import re
import sys
import threading
from dataclasses import dataclass, field

from openai import OpenAI

from wsp_poc.extract_wsp import build_document
from wsp_poc.validate_wsp import (EMBEDDING_DIMS, MemoryEmbeddingCache, NumpyRetriever,
                                  OpenAIEmbedding, WspChunker, count_tokens)
from wsp_poc.vector_store import QdrantEmbeddingCache, QdrantRetriever, QdrantVectorStore

_INDEXES = {}
_LOCK = threading.Lock()


def file_sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


@dataclass
class EvidenceIndex:
    doc_id: str
    source_path: str
    text: str
    pages: int
    chunks: list
    total_tokens: int
    retriever: object = None
    embedder: object = None
    backend: str = "none"
    position: dict = field(default_factory=dict)      # chunk_id -> index in chunks

    def by_id(self, chunk_id):
        return self.chunks[self.position[chunk_id]]


def _open_store(settings, model):
    if settings.qdrant_url.lower() == "none":
        return None
    store = QdrantVectorStore(settings.qdrant_url, settings.collection_prefix,
                              model, EMBEDDING_DIMS[model])
    store.wait_ready()
    store.ensure_collections()
    return store


def ingest(pdf_path, settings, meter, api_key, dry_run=False):
    """Extract, chunk, embed and index one evidence PDF. Cached per content hash."""
    doc_id = "ev_" + file_sha256(pdf_path)[:12]
    with _LOCK:
        cached = _INDEXES.get(doc_id)
        if cached is not None and (dry_run or cached.retriever is not None):
            print(f"evidence {doc_id}: in-process cache hit ({len(cached.chunks)} chunks)",
                  file=sys.stderr)
            return cached

    text, pages = build_document(pdf_path)
    chunker = WspChunker(doc_id)
    chunks = chunker.chunk(text)
    if not chunks:
        raise RuntimeError(f"no chunks produced from {pdf_path} -- is it text-native?")
    total = sum(c.tokens for c in chunks)
    index = EvidenceIndex(doc_id=doc_id, source_path=pdf_path, text=text, pages=pages,
                          chunks=chunks, total_tokens=total,
                          position={c.chunk_id: i for i, c in enumerate(chunks)})
    print(f"evidence {doc_id}: {pages} pages, {len(chunks)} chunks, {total:,} tokens "
          f"({chunker.toc_pages_dropped} TOC-ish pages dropped)", file=sys.stderr)
    if dry_run:
        with _LOCK:
            _INDEXES[doc_id] = index
        return index

    client = OpenAI(api_key=api_key)
    store = _open_store(settings, settings.embedding_model)
    cache = QdrantEmbeddingCache(store) if store is not None else MemoryEmbeddingCache()
    embedder = OpenAIEmbedding(client, settings.embedding_model, meter, cache)
    vectors = embedder.embed([WspChunker.embed_text(c) for c in chunks])
    if store is not None:
        retriever = QdrantRetriever(store, chunks, gap_floor=0.0, top_k=settings.top_k)
        retriever.index(vectors)
        index.backend = "qdrant"
    else:
        retriever = NumpyRetriever(chunks, vectors, gap_floor=0.0, top_k=settings.top_k)
        index.backend = "numpy"
    index.retriever = retriever
    index.embedder = embedder
    with _LOCK:
        _INDEXES[doc_id] = index
    return index


def get_index(doc_id):
    index = _INDEXES.get(doc_id)
    if index is None:
        raise RuntimeError(f"evidence {doc_id} is not ingested in this process")
    return index


def retrieve(index, queries, top_k, radius, max_tokens):
    """Rank chunks for a step (max over query embeddings), expand each hit to its
    neighbours, and return the survivors in document order.

    Neighbour expansion matters for absence checks: the sentence that *should*
    name a successor for the CCO sits in the same section as the roles it does
    name, and a 650-token chunk boundary can split them.
    """
    vectors = index.embedder.embed(queries)
    index.retriever.top_k = top_k
    ranked = index.retriever.rank(vectors)
    scores = {c.chunk_id: s for c, s in ranked}
    chosen, tokens = [], 0
    for chunk, _ in ranked:                       # best first, so the cap drops the weakest
        pos = index.position[chunk.chunk_id]
        for j in range(max(0, pos - radius), min(len(index.chunks), pos + radius + 1)):
            candidate = index.chunks[j]
            if candidate.chunk_id in chosen:
                continue
            if tokens + candidate.tokens > max_tokens:
                continue
            chosen.append(candidate.chunk_id)
            tokens += candidate.tokens
    ordered = sorted(chosen, key=lambda cid: index.position[cid])
    return [(index.by_id(cid), scores.get(cid)) for cid in ordered], ranked


_STOP = set("the a an and or of to for in on at by with is are be that this it as from its "
            "confirm verify obtain ensure exist exists documented available identified".split())


def lexical_retrieve(index, queries, top_k, radius, max_tokens):
    """Embedding-free stand-in for retrieve(), used by --dry-run so the prompt-size
    estimate reflects a realistic context rather than a guess. Scores chunks by
    query-term overlap; the same neighbour expansion and token cap apply."""
    terms = {w for q in queries for w in re.findall(r"[a-z]{3,}", q.lower())} - _STOP
    scored = []
    for chunk in index.chunks:
        words = set(re.findall(r"[a-z]{3,}", chunk.text.lower()))
        hits = len(terms & words)
        scored.append((chunk, hits / (len(terms) or 1)))
    ranked = sorted(scored, key=lambda cs: (-cs[1], index.position[cs[0].chunk_id]))[:top_k]
    scores = {c.chunk_id: s for c, s in ranked}
    chosen, tokens = [], 0
    for chunk, _ in ranked:
        pos = index.position[chunk.chunk_id]
        for j in range(max(0, pos - radius), min(len(index.chunks), pos + radius + 1)):
            candidate = index.chunks[j]
            if candidate.chunk_id in chosen or tokens + candidate.tokens > max_tokens:
                continue
            chosen.append(candidate.chunk_id)
            tokens += candidate.tokens
    ordered = sorted(chosen, key=lambda cid: index.position[cid])
    return [(index.by_id(cid), scores.get(cid)) for cid in ordered], ranked


def full_context(index):
    return [(c, None) for c in index.chunks]


def format_excerpts(scored_chunks):
    lines = []
    for chunk, score in scored_chunks:
        sim = f" | similarity {score:.3f}" if score is not None else ""
        lines.append(f"\n--- {chunk.chunk_id}{sim} | pages {chunk.page_start}-{chunk.page_end} | "
                     f"{' > '.join(chunk.heading_path) or '(untitled)'} ---\n{chunk.text}")
    return "\n".join(lines)


def context_tokens(scored_chunks):
    return sum(c.tokens for c, _ in scored_chunks)


def estimate_tokens(text):
    return count_tokens(text)
