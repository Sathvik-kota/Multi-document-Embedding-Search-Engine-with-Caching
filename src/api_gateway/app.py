# api_gateway/app.py

from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os

app = FastAPI(title="API Gateway")

# --------------------------
# Microservice URLs
# --------------------------
DOC_URL = "http://localhost:9001"
EMBED_URL = "http://localhost:9002"
SEARCH_URL = "http://localhost:9003"
EXPLAIN_URL = "http://localhost:9004"

DATA_FOLDER = "data/docs"


# --------------------------
# Models
# --------------------------
class SearchQuery(BaseModel):
    query: str
    top_k: int = 5


# --------------------------
# Load all documents
# --------------------------
@app.post("/load_documents")
def load_documents():
    resp = requests.post(f"{DOC_URL}/load_docs",
                         json={"folder": DATA_FOLDER})
    return resp.json()


# --------------------------
# Build Everything (docs + embeddings + index)
# --------------------------
@app.post("/initialize")
def initialize():
    # 1) Load docs
    docs_resp = requests.post(f"{DOC_URL}/load_docs",
                              json={"folder": DATA_FOLDER}).json()

    docs = docs_resp.get("documents", [])

    # 2) Embed batch
    embed_resp = requests.post(
        f"{EMBED_URL}/embed_batch",
        json={"docs": docs}
    ).json()

    # Extract embeddings + metadata for index
    embeddings = [item["embedding"] for item in embed_resp["results"]]
    meta = {i: item["filename"] for i, item in enumerate(embed_resp["results"])}

    # 3) Build FAISS index
    index_resp = requests.post(
        f"{SEARCH_URL}/build_index",
        json={"embeddings": embeddings, "meta": meta}
    ).json()

    return {
        "docs_loaded": len(docs),
        "embeddings": len(embeddings),
        "index": index_resp
    }


# --------------------------
# MAIN SEARCH
# --------------------------
@app.post("/search")
def search(req: SearchQuery):

    # --------------------------
    # 1) Embed Query
    # --------------------------
    try:
        q_resp = requests.post(
            f"{EMBED_URL}/embed_document",
            json={"filename": "query", "text": req.query, "hash": "query"},
            timeout=10
        )

        if q_resp.status_code != 200:
            return {"error": f"Embed service failed: {q_resp.text}"}

        q_emb = q_resp.json()["embedding"]

    except Exception as e:
        return {"error": f"Query embedding failed: {str(e)}"}

    # --------------------------
    # 2) Search vectors
    # --------------------------
    try:
        s_resp = requests.post(
            f"{SEARCH_URL}/search_vectors",
            json={"query_embedding": q_emb, "top_k": req.top_k},
            timeout=10
        )

        if s_resp.status_code != 200:
            return {"error": f"Search service failed: {s_resp.text}"}

        s_data = s_resp.json()

    except Exception as e:
        return {"error": f"Vector search failed: {str(e)}"}

    scores = s_data["scores"]
    indices = s_data["indices"]
    meta = s_data["meta"]  # { "0": "fileA.txt", ... }

    # --------------------------
    # 3) Load docs again to get text
    # --------------------------
    docs_resp = requests.post(f"{DOC_URL}/load_docs",
                              json={"folder": DATA_FOLDER}).json()
    docs = docs_resp.get("documents", [])

    # Convert list → dict for fast lookup
    doc_map = {d["filename"]: d for d in docs}

    # --------------------------
    # 4) Explain each result
    # --------------------------
    results = []

    for i, score in zip(indices, scores):
        i = int(i)
        filename = meta[str(i)]

        doc_item = doc_map.get(filename)

        if doc_item is None:
            continue

        try:
            exp_resp = requests.post(
                f"{EXPLAIN_URL}/explain",
                json={
                    "query": req.query,
                    "document_text": doc_item["clean_text"]
                },
                timeout=10
            )

            explanation = exp_resp.json() if exp_resp.status_code == 200 else {}

        except:
            explanation = {}

        results.append({
            "filename": filename,
            "score": score,
            "preview": doc_item["clean_text"][:350],
            "explanation": explanation
        })

    return {"results": results}
