# src/search_service/app.py
from fastapi import FastAPI
from pydantic import BaseModel
from .indexer import FAISSIndexer
import numpy as np

app = FastAPI(title="Search Service")

indexer = FAISSIndexer()
# attempt load if exists
indexer.try_load()

class BuildIndexRequest(BaseModel):
    embeddings: list
    meta: dict

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
    if indexer.index is None:
        return {"error": "index_not_built"}
    query = np.array(req.query_embedding, dtype="float32")
    scores, ids = indexer.search(query, req.top_k)
    return {"scores": scores, "ids": ids, "meta": indexer.meta}
