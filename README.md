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
- **FAISS Vector Search + Persistent Storage**
- **LLM-Driven Explanations (Gemini 2.5 Flash)**
- **Google-Gemini-Style Streamlit UI**
- **Real Microservice Architecture**
- **Full Evaluation Suite (Accuracy · MRR · nDCG)**

A complete end-to-end ML system demonstrating real-world architecture & search engineering.

---

#  Features

## 🔹 Core Search

- Embedding-based semantic search over `.txt` documents  
- FAISS `IndexFlatL2` on **normalized vectors** (≈ cosine similarity)  
- Top-K ranking + similarity scores  
- Keyword overlap, overlap ratio  
- Top semantic sentences  
- Full-text preview  

---

## 🔹 Microservice Architecture (5 FastAPI Services)

Each component runs as an **independent microservice**, mirroring real production systems:

| Service | Responsibility |
|--------|----------------|
| **doc_service** | Load, clean, normalize, hash, and store documents |
| **embed_service** | MiniLM embedding generation + caching |
| **search_service** | FAISS index build, update, and vector search |
| **explain_service** | Keyword overlap, top sentences, LLM explanations |
| **api_gateway** | Orchestration: a clean unified API for the UI |
| **streamlit_ui** | Gemini-style user interface |

This separation supports **scalability**, **fault isolation**, and **independent service upgrades** — *like real enterprise ML platforms*.

---

## 🔹 Explanations

Every search result includes:

- **Keyword overlap**
- **Semantic overlap ratio**
- **Top relevant sentences (MiniLM sentence similarity)**
- **LLM-generated explanation**:  
  “Why did this document match your query?”

---

## 🔹 Evaluation Suite
A built-in evaluation workflow providing:

- **Accuracy**
- **MRR (Mean Reciprocal Rank)**
- **nDCG@K**
- Correct vs Incorrect queries  
- Per-query detailed table  


---

#  How Caching Works (MANDATORY SECTION)

Caching happens inside **`embed_service/cache_manager.py`**.

### ✔ Zero repeated embeddings  
Each document is fingerprinted using:

- **filename**
- **MD5(cleaned_text)**

If the hash matches a previously stored file:
- cached embedding is loaded instantly  
- prevents costly re-embedding  
- improves startup & query latency  

### Cache Files:
- `cache/embed_meta.json` → mapping of filename → `{hash, index}`
- `cache/embeddings.npy` → matrix of all embeddings

### Benefits
- Startup: **5–10 seconds → <1 second**
- Low compute cost  
- Ideal for Hugging Face Spaces  
- Guarantees reproducible results  

---

#  FAISS Persistence (Warm Start Optimization)

This project saves BOTH embeddings and FAISS index:

- `cache/embeddings.npy`  
- `cache/embed_meta.json`  
- `faiss_index.bin`  
- `faiss_meta.pkl`  

On startup:search_service.indexer.try_load()


If found → loaded instantly.  
If not → FAISS index is rebuilt from cached embeddings.

### Why this matters?
- Makes FAISS behave like a **persistent vector database**  
- Extremely important for **Docker**, **Spaces**, and **cold restarts**  
- Zero delay in rebuilding large indexes  

---

#  Folder Structure 
```
├── 📁 src
│ ├── 📁 doc_service
│ │ ├── init.py
│ │ ├── app.py
│ │ └── utils.py
│ │
│ ├── 📁 embed_service
│ │ ├── init.py
│ │ ├── app.py
│ │ ├── embedder.py
│ │ └── cache_manager.py
│ │
│ ├── 📁 search_service
│ │ ├── init.py
│ │ ├── app.py
│ │ └── indexer.py
│ │
│ ├── 📁 explain_service
│ │ ├── init.py
│ │ ├── app.py
│ │ └── explainer.py
│ │
│ ├── 📁 api_gateway
│ │ ├── init.py
│ │ └── app.py
│ │
│ └── 📁 ui
│ └── streamlit_app.py
│
├── 📁 data
│ └── 📁 docs
│ └── (your .txt documents)
│
├── 📁 cache
│ ├── embed_meta.json
│ ├── embeddings.npy
│ ├── faiss_index.bin
│ └── faiss_meta.pkl
│
├── 📁 eval
│ ├── evaluate.py
│ └── generated_queries.json
│
├── start.sh
├── Dockerfile
├── requirements.txt
├── .gitignore
└── README.md

```
---

#  How to Run Embedding Generation

Embeddings generate automatically during initialization:


Pipeline:

1. **doc_service** → load + clean + hash  
2. **embed_service** → create or load cached embeddings  
3. **search_service** → FAISS index build or load  
4. Return summary  


---

#  How to Start the API 

All services are launched using:

```bash
bash start.sh

This starts:

9001 → doc_service

9002 → embed_service

9003 → search_service

9004 → explain_service

8000 → api_gateway

7860 → Streamlit UI
```
---

##  Architecture Overview

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



---

##  Design Choices

### 1️⃣ **Microservices instead of Monolithic**
- Real-world ML systems separate **indexing, embedding, routing, and inference**.
- Enables **independent scaling**, easier debugging, and service-level isolation.


---

### 2️⃣ **MiniLM Embeddings**
-  **Fast on CPU** (optimized for lightweight inference)
- **High semantic quality** for short & long text
- **Small model** → ideal for search engines, mobile, Spaces deployments

---

### 3️⃣ **FAISS L2 on Normalized Embeddings**
L2 distance is used instead of cosine because:

- **FAISS FlatL2 is faster** and more optimized
- When vectors are normalized:  
  `L2 Distance ≡ Cosine Distance` (mathematically equivalent)
-  Avoids the overhead of cosine kernels

---

### 4️⃣ **Local Embedding Cache**
- Reduces startup time from **~5 seconds → <1 second**
- Prevents **re-embedding identical documents**
-Allows FAISS persistence to work smoothly
- Speeds up startup & indexing
---
### 5️⃣FAISS Persistence (Warm Start Optimization)
- Eliminates the need to rebuild index on each startup
- Warm-loads instantly at startup
- Ideal for Spaces & Docker environments
- A lightweight vector-database
---
### 6️⃣ **LLM-Driven Explainability**
- Generates **human-friendly reasoning**. Makes search results more interpretable and intelligent.
- Explains **why a document matched your query**
- Combines:
  - Top semantic-matching sentences  
  - Keyword overlap  
  - Gemini’s natural-language reasoning  

---

### 7️⃣ **Streamlit for Fast UI**
-  Instant reload during development  
-  Clean layout 
- Easy to extend (evaluation panel, metrics, expanders)





