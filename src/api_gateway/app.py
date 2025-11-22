# app.py
import requests
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="API Gateway")

# -------------------------------
# Microservice Endpoints (local)
# -------------------------------
DOC_SERVICE_URL = "http://localhost:9001"
EMBED_SERVICE_URL = "http://localhost:9002"
SEARCH_SERVICE_URL = "http://localhost:9003"
EXPLAIN_SERVICE_URL = "http://localhost:9004"


# -------------------------------
# Request models
# -------------------------------
class IndexRequest(BaseModel):
    folder: str


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


# ==============================================
# 1) INDEXING PIPELINE
# ==============================================
@app.post("/index")
def index_documents(req: IndexRequest):

    # 1. Load docs from doc_service
    doc_res = requests.post(
        f"{DOC_SERVICE_URL}/load_docs",
        json={"folder": req.folder}
    ).json()

    docs = doc_res["documents"]

    # 2. Send to embed_service batch embed
    embed_payload = {"docs": []}
    for d in docs:
        embed_payload["docs"].append({
            "filename": d["filename"],
            "text": d["clean_text"],
            "hash": d["hash"]
        })

    embed_res = requests.post(
        f"{EMBED_SERVICE_URL}/embed_batch",
        json=embed_payload
    ).json()

    # 3. Prepare FAISS build request
    meta_map = {}
    embeddings = []

    for item in embed_res["results"]:
        fname = item["filename"]
        meta_map[fname] = { "index": len(embeddings) }
        embeddings.append(item["embedding"])

    # 4. Build FAISS index via search_service
    build_res = requests.post(
        f"{SEARCH_SERVICE_URL}/build_index",
        json={"embeddings": embeddings, "meta": meta_map}
    ).json()

    return {
        "documents_indexed": len(embeddings),
        "build_status": build_res
    }


# ==============================================
# 2) SEARCH PIPELINE
# ==============================================
@app.post("/search")
def search(req: SearchRequest):

    # 1. Embed query
    q_res = requests.post(
        f"{EMBED_SERVICE_URL}/embed_document",
        json={
            "filename": "query",
            "text": req.query,
            "hash": "query"
        }
    ).json()

    q_emb = q_res["embedding"]

    # 2. Vector search
    search_res = requests.post(
        f"{SEARCH_SERVICE_URL}/search_vectors",
        json={"query_embedding": q_emb, "top_k": req.top_k}
    ).json()

    scores = search_res["scores"]
    ids = search_res["indices"]
    meta = search_res["meta"]

    # 3. Map doc_id → filename
    filenames = list(meta.keys())
    final_results = []

    # 4. Retrieve text & get explanation for each doc
    for score, idx in zip(scores, ids):
        if idx == -1:
            continue

        filename = filenames[idx]

        # Fetch original text from doc_service
        # (We re-load the document to get preview + explanation)
        doc_text = open(f"../../data/docs/{filename}", "r").read()

        # Get explanation from explain_service
        exp_res = requests.post(
            f"{EXPLAIN_SERVICE_URL}/explain",
            json={
                "query": req.query,
                "document_text": doc_text
            }
        ).json()

        final_results.append({
            "filename": filename,
            "score": score,
            "explanation": exp_res,
            "preview": doc_text[:300]  # small snippet
        })

    return {
        "query": req.query,
        "top_k": req.top_k,
        "results": final_results
    }
