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
class SearchRequest(BaseModel):
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
def search(req: SearchRequest):

    # 1) Load documents
    docs = requests.post(f"{DOC_SERVICE}/load_docs", json={"folder": DATA_FOLDER}).json()["documents"]

    # 2) Embed docs
    embed_resp = requests.post(f"{EMBED_SERVICE}/embed_all", json=docs).json()
    embeddings = [x["embedding"] for x in embed_resp["results"]]
    meta = {i: x["filename"] for i, x in enumerate(embed_resp["results"])}

    # 3) Build FAISS index
    requests.post(f"{SEARCH_SERVICE}/build_index", json={"embeddings": embeddings, "meta": meta})

    # 4) Embed query
    q = requests.post(f"{EMBED_SERVICE}/embed_document",
                      json={"filename": "query", "text": req.query, "hash": "0"}).json()
    query_emb = q["embedding"]

    # 5) Vector search
    search_out = requests.post(f"{SEARCH_SERVICE}/search_vectors",
                               json={"query_embedding": query_emb, "top_k": req.top_k}).json()

    # 6) Explain each result
    results = []
    for idx, score in zip(search_out["ids"], search_out["scores"]):
        filename = search_out["meta"][str(idx)]
        doc_text = requests.post(f"{DOC_SERVICE}/load_docs", json={"folder": DATA_FOLDER}).json()["documents"]

        doc_item = [d for d in doc_text if d["filename"] == filename][0]

        explanation = requests.post(f"{EXPLAIN_SERVICE}/explain",
                                    json={"query": req.query, "document_text": doc_item["clean_text"]}).json()

        results.append({
            "filename": filename,
            "score": score,
            "explanation": explanation,
            "preview": doc_item["clean_text"][:400]
        })

    return {"results": results}
