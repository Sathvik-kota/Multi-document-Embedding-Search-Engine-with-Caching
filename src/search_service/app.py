# search_service/app.py

from fastapi import FastAPI
from pydantic import BaseModel
from .indexer import FAISSIndexer
import numpy as np

app = FastAPI(title="Search Service")

indexer = FAISSIndexer()

# Load cached embeddings + meta on startup (if available)
meta, embs = indexer.try_load()
if embs is not None:
    indexer.build(embs, meta)
    print(f"⚡ LOADED EXISTING FAISS INDEX with {embs.shape[0]} vectors")
else:
    print("⚠️ No saved index found.")


# -------------------------------------------------------
# FIXED: build_index WITHOUT request body
# Pulls embeddings from cache_manager automatically
# -------------------------------------------------------
@app.post("/build_index")
def build_index():
    """
    Build FAISS index using cached embeddings.
    DOES NOT require a JSON body.
    """

    meta, embs = indexer.try_load()
    if embs is None:
        return {"status": "error", "message": "No embeddings found. Run /embed_all first."}

    indexer.build(embs, meta)

    return {
        "status": "index_built",
        "count": embs.shape[0],
        "dim": embs.shape[1]
    }


# -------------------------------------------------------
# SEARCH ENDPOINT (works with gateway + streamlit)
# -------------------------------------------------------
class SearchRequest(BaseModel):
    query_embedding: list
    top_k: int = 5


@app.post("/search_vectors")
def search_vectors(req: SearchRequest):

    if indexer.index is None:
        raise ValueError("FAISS index is not loaded!")

    query_emb = np.array(req.query_embedding, dtype="float32").reshape(1, -1)

    scores, ids = indexer.search(query_emb, req.top_k)

    return {
        "scores": scores.tolist(),
        "indices": ids.tolist(),
        "meta": indexer.meta      # filename lookup
    }
