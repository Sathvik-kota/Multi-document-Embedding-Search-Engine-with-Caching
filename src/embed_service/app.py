# app.py
from fastapi import FastAPI
from pydantic import BaseModel
from .embedder import Embedder
from .cache_manager import CacheManager

app = FastAPI(title="Embed Service")

embedder = Embedder()
cache = CacheManager()

# -------------------------
# Embed single document
# -------------------------
class EmbedRequest(BaseModel):
    filename: str
    text: str
    hash: str

@app.post("/embed_document")
def embed_document(req: EmbedRequest):
    if cache.exists(req.filename, req.hash):
        emb = cache.get_embedding(req.filename)
        return {"filename": req.filename, "cached": True, "embedding": emb.tolist()}

    emb = embedder.embed_text(req.text)
    cache.add_embedding(req.filename, req.hash, emb)

    return {"filename": req.filename, "cached": False, "embedding": emb.tolist()}

# -------------------------
# Embed batch of documents
# -------------------------
class BatchEmbedRequest(BaseModel):
    docs: list  # list of dicts

@app.post("/embed_batch")
def embed_batch(req: BatchEmbedRequest):
    results = []
    new_texts, new_files, new_hashes = [], [], []

    for d in req.docs:
        if cache.exists(d["filename"], d["hash"]):
            results.append({
                "filename": d["filename"],
                "cached": True,
                "embedding": cache.get_embedding(d["filename"]).tolist()
            })
        else:
            new_texts.append(d["text"])
            new_files.append(d["filename"])
            new_hashes.append(d["hash"])

    if new_texts:
        new_embs = embedder.embed_batch(new_texts)
        for fname, h, emb in zip(new_files, new_hashes, new_embs):
            cache.add_embedding(fname, h, emb)
            results.append({
                "filename": fname,
                "cached": False,
                "embedding": emb.tolist()
            })

    return {"count": len(results), "results": results}

# -------------------------
# Get all embeddings
# -------------------------
@app.get("/all_embeddings")
def get_all_embeddings():
    meta, embs = cache.all_embeddings()
    return {"meta": meta, "embeddings": embs.tolist()}

# -------------------------
# NEW FIXED ENDPOINT
# -------------------------
@app.post("/embed_all")
def embed_all_docs(docs: list):
    """
    API Gateway sends raw docs directly.
    docs = [
       {"filename": ..., "clean_text": ..., "hash": ...}
    ]
    """
    batch = {"docs": [{"filename": d["filename"], "text": d["clean_text"], "hash": d["hash"]} for d in docs]}
    result = embed_batch(BatchEmbedRequest(**batch))
    return result
