# app.py
from fastapi import FastAPI
from pydantic import BaseModel
from indexer import FAISSIndexer
import numpy as np

app = FastAPI(title="Search Service")

indexer = FAISSIndexer()
meta = indexer.load()   # loads metadata on startup


class BuildIndexRequest(BaseModel):
    embeddings: list    # list of embedding vectors
    meta: dict          # filename → index position mapping


@app.post("/build_index")
def build_index(req: BuildIndexRequest):
    embeddings = np.array(req.embeddings, dtype="float32")

    indexer.build(embeddings, req.meta)

    return {"status": "index_built", "count": embeddings.shape[0]}


class SearchRequest(BaseModel):
    query_embedding: list
    top_k: int = 5


@app.post("/search_vectors")
def search_vectors(req: SearchRequest):
    query_emb = np.array(req.query_embedding, dtype="float32")

    scores, ids = indexer.search(query_emb, req.top_k)

    return {
        "scores": scores.tolist(),
        "indices": ids.tolist(),
        "meta": meta
    }
