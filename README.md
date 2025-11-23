---
title: Document Search Engine 
emoji: 📄
colorFrom: blue
colorTo: purple
sdk: docker
sdk_version: "0.0.0"
app_file: start.sh
pinned: false
---

#  Multi-Document Semantic Search Engine 
A **production-inspired multi-microservice semantic search system** built over 20+ text documents.

Designed with:
- **Sentence-Transformers** (`all-MiniLM-L6-v2`)
- **Local Embedding Cache**
- **FAISS vector search + persistent storage**
- **LLM-Driven Explanations** (Gemini 2.5 Flash)
- **Google-Gemini-Style Streamlit UI**
- **Microservice Architecture**
- **Full Evaluation Suite**: Accuracy · MRR · nDCG

Showcasing real-world architecture and ML system design.

---

## 🚀 Features

### 🔹 Core Search

- Embedding-based semantic search over `.txt` docs
- FAISS `IndexFlatL2` on normalized vectors 
- Top-K ranking + score display
- Keyword overlap, overlap ratio, top matching sentences

### 🔹 Microservice Architecture 

Each logical component runs as a **separate FastAPI microservice**:

| Service | Responsibility |
|--------|----------------|
| **doc_service** | Load + clean + hash documents |
| **embed_service** | MiniLM embeddings + caching |
| **search_service** | FAISS index build + vector search |
| **explain_service** | Keyword overlap + top sentences + LLM reasoning |
| **api_gateway** | Full pipeline orchestration |
| **streamlit_ui** | Gemini-styled user interface |

This mirrors real production designs (scalable, modular, interchangeable components).

### 🔹 Explanations

For each search result you get:

- Why this document was matched (LLM explanation)
- Which keywords overlapped (simple heuristic)
- Overlap ratio (0–1)
- Top matching sentences (semantic similarity)

---
### 🔹 **Evaluation Suite**
Metrics included:
- **Accuracy**
- **MRR (Mean Reciprocal Rank)**
- **nDCG@K**
- **Per-query table**
- **Correct vs Incorrect Fetches**

---
# ⚡ How Caching Works 
Caching happens inside **`embed_service/cache_manager.py`**.

### ✔ Prevents re-embedding unchanged files  
Each document is identified by: filename + MD5(clean_text)

If `(filename, hash)` already exists:
- the embedding is **loaded instantly**
- avoids recomputing MiniLM embeddings
- makes repeated runs extremely fast

### Cache contents:
- `cache/embed_meta.json` → maps filename → `{"hash": "...", "index": int}`
- `cache/embeddings.npy` → stacked embedding matrix

Caching benefits:
- Faster startup  
- Faster user queries  
- Less compute usage  
- More production-ready  

---

# 🧠 How to Run Embedding Generation 
### Embedding happens automatically during **initialization**:

`POST /initialize` (handled by API Gateway):

1. Load all docs from `data/docs`
2. Send batch clean texts → **embed_service**
3. Cache manager stores new embeddings
4. FAISS index built in **search_service**

### Manual Embedding (Optional)

You can call:
POST /embed_batch
POST /embed_document

---
### 🧩 FAISS Persistence (Warm Start Optimization)

The system stores embeddings **and** the FAISS vector index on disk:

- `cache/embeddings.npy` → all stored embeddings  
- `cache/embed_meta.json` → filename → hash → embedding index  
- `faiss_index.bin` → saved FAISS index  
- `faiss_meta.pkl` → mapping of FAISS row → document filename  

On startup, the `search_service` automatically runs:

---

##  Design Choices

### 1️⃣ **Microservices instead of Monolithic**
- Real-world ML systems separate **indexing, embedding, routing, and inference**.
- Enables **independent scaling**, easier debugging, and service-level isolation.


---

### 2️⃣ **MiniLM Embeddings**
- ⚡ **Fast on CPU** (optimized for lightweight inference)
- 🎯 **High semantic quality** for short & long text
- 🪶 **Small model** → ideal for search engines, mobile, Spaces deployments

---

### 3️⃣ **FAISS L2 on Normalized Embeddings**
L2 distance is used instead of cosine because:

- 🚀 **FAISS FlatL2 is faster** and more optimized
- ✨ When vectors are normalized:  
  `L2 Distance ≡ Cosine Distance` (mathematically equivalent)
- 🧩 Avoids the overhead of cosine kernels

---

### 4️⃣ **Local Embedding Cache**
- Reduces startup time from **~5 seconds → <1 second**
- Prevents **re-embedding identical documents**
- Stores:
  - `embed_meta.json` → filename → hash → index
  - `embeddings.npy` → matrix of stored embeddings
- Saves compute + makes repeated searches much faster

---

### 5️⃣ **LLM-Driven Explainability**
- Generates **human-friendly reasoning**
- Explains **why a document matched your query**
- Combines:
  - Top semantic-matching sentences  
  - Keyword overlap  
  - Gemini’s natural-language reasoning  

---

### 6️⃣ **Streamlit for Fast UI**
- ⚡ Instant reload during development  
- 🎨 Clean layout 
- 🧱 Easy to extend (evaluation panel, metrics, expanders)



## 🏗️ Architecture Overview

### High-level Flow

1. User asks a question in **Streamlit UI**
2. UI sends request → **API Gateway** `/search`
3. Gateway:
   - Embeds query via **Embed Service**
   - Searches FAISS via **Search Service**
   - Fetches full doc text from **Doc Service**
   - Gets explanation from **Explain Service**
4. Response returned to UI with:
   - filename, score, preview, full text
   - keyword overlap, overlap ratio
   - top matching sentences
   - optional LLM explanation

