# src/embed_service/app.py
from fastapi import FastAPI
from pydantic import BaseModel
from src.embed_service.embedder import Embedder
from src.embed_service.cache_manager import CacheManager

import numpy as np

app = FastAPI(title="Embed Service")

embedder = Embedder()
cache = CacheManager()

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

class BatchEmbedRequest(BaseModel):
    docs: list

@app.post("/embed_batch")
def embed_batch(req: BatchEmbedRequest):
    results = []
    new_texts, new_files, new_hashes = [], [], []
    for d in req.docs:
        filename = d.get("filename")
        file_hash = d.get("hash")
        text = d.get("text") or d.get("clean_text") or ""
        if cache.exists(filename, file_hash):
            results.append({"filename": filename, "cached": True, "embedding": cache.get_embedding(filename).tolist()})
        else:
            new_files.append(filename)
            new_hashes.append(file_hash)
            new_texts.append(text)

    if new_texts:
        new_embs = embedder.embed_batch(new_texts)
        for fname, h, emb in zip(new_files, new_hashes, new_embs):
            cache.add_embedding(fname, h, emb)
            results.append({"filename": fname, "cached": False, "embedding": emb.tolist()})

    return {"count": len(results), "results": results}

@app.get("/all_embeddings")
def get_all_embeddings():
    meta, embs = cache.all_embeddings()
    return {"meta": meta, "embeddings": embs.tolist()}

# convenience endpoint called earlier by older code
@app.post("/embed_all")
def embed_all_docs(docs: list):
    # docs: list of {filename, clean_text, hash}
    batch = {"docs": [{"filename": d["filename"], "text": d.get("clean_text") or d.get("text", ""), "hash": d["hash"]} for d in docs]}
    return embed_batch(BatchEmbedRequest(**batch))
