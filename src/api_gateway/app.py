# api_gateway/app.py

from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI(title="API Gateway")


# ------------------------------
# Service URLs
# ------------------------------
DOC_SERVICE = "http://localhost:9001"
EMBED_SERVICE = "http://localhost:9002"
SEARCH_SERVICE = "http://localhost:9003"
EXPLAIN_SERVICE = "http://localhost:9004"


# ------------------------------
# Search request model
# ------------------------------
class SearchQuery(BaseModel):
    query: str
    top_k: int = 5


# ------------------------------
# Gateway: Load Documents
# ------------------------------
@app.post("/load_documents")
def load_documents():
    resp = requests.post(f"{DOC_SERVICE}/load_docs", json={"folder": "data/docs"})
    return resp.json()


# ------------------------------
# Gateway: Generate ALL Embeddings
# ------------------------------
@app.post("/generate_embeddings")
def generate_embeddings():
    resp = requests.post(f"{EMBED_SERVICE}/embed_all")
    return resp.json()


# ------------------------------
# Gateway: Build FAISS index
# ------------------------------
@app.post("/build_index")
def build_index():
    resp = requests.post(f"{SEARCH_SERVICE}/build_index")
    return resp.json()


# ------------------------------
# Gateway: Search + Explanation
# ------------------------------
@app.post("/search")
def search(req: SearchQuery):

    # 1️⃣ Embed the query
    embed_resp = requests.post(
        f"{EMBED_SERVICE}/embed_document",
        json={"filename": "query", "text": req.query, "hash": "query"}
    ).json()

    query_emb = embed_resp["embedding"]

    # 2️⃣ Search FAISS index
    search_resp = requests.post(
        f"{SEARCH_SERVICE}/search_vectors",
        json={"query_embedding": query_emb, "top_k": req.top_k}
    ).json()

    scores = search_resp["scores"][0]
    ids = search_resp["indices"][0]
    meta = search_resp["meta"]  # filename lookup

    # 3️⃣ For each result → fetch doc text + explanation
    results = []
    for score, idx in zip(scores, ids):
        filename = list(meta.keys())[list(meta.values()).index(idx)]

        # pull original document text
        doc_text_resp = requests.get(f"{DOC_SERVICE}/get_doc/{filename}").json()["text"]

        # explanation
        explain_resp = requests.post(
            f"{EXPLAIN_SERVICE}/explain",
            json={"query": req.query, "document_text": doc_text_resp}
        ).json()

        results.append({
            "filename": filename,
            "score": score,
            "explanation": explain_resp,
            "preview": doc_text_resp[:200] + "..."
        })

    return {"results": results}
