from fastapi import FastAPI
from pydantic import BaseModel
from .indexer import FAISSIndexer
import numpy as np

app = FastAPI(title="Search Service")

indexer = FAISSIndexer()

# -------------------------
# Build FAISS index
# -------------------------
class BuildIndexRequest(BaseModel):
    embeddings: list
    meta: dict

@app.post("/build_index")
def build_index(req: BuildIndexRequest):
    embeddings = np.array(req.embeddings, dtype="float32")
    indexer.build(embeddings, req.meta)
    return {"status": "index_built", "count": len(req.embeddings)}

# -------------------------
# Search
# -------------------------
class SearchRequest(BaseModel):
    query_embedding: list
    top_k: int = 5

@app.post("/search_vectors")
def search_vectors(req: SearchRequest):
    if not indexer.index:
        raise ValueError("FAISS index not built!")

    query = np.array(req.query_embedding, dtype="float32")
    scores, ids = indexer.search(query, req.top_k)

    return {"scores": scores.tolist(), "ids": ids.tolist(), "meta": indexer.meta}
