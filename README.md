---
title: Document Search Engine (Gemini Style)
emoji: 📄
colorFrom: blue
colorTo: purple
sdk: docker
sdk_version: "0.0.0"
app_file: start.sh
pinned: false
---

# 🔍 Multi-Document Semantic Search Engine (Gemini-Style UI)

A **microservice-based** semantic search engine over 20 Newsgroups-style text documents with:

- Sentence-Transformers embeddings (`all-MiniLM-L6-v2`)
- **Local caching** (no repeated embedding computation)
- **FAISS** vector index (L2 on normalized embeddings)
- **LLM-powered explanations** (Gemini 2.5 Flash, optional)
- **Streamlit UI** styled like **Google Gemini**
- Full **evaluation suite** (Accuracy, MRR, nDCG, per-query breakdown)

---

## 🚀 Features

### 🔹 Core Search

- Embedding-based semantic search over `.txt` docs
- FAISS `IndexFlatL2` on normalized vectors (≈ cosine similarity)
- Top-K ranking + score display
- Keyword overlap, overlap ratio, top matching sentences

### 🔹 Microservice Architecture (Your Big Idea 💡)

Each logical component runs as a **separate FastAPI microservice**:

- `doc_service` – loads & preprocesses documents
- `embed_service` – generates + caches embeddings
- `search_service` – maintains FAISS index & vector search
- `explain_service` – gives explanations (keywords + Gemini LLM)
- `api_gateway` – orchestrates everything behind a clean API
- `streamlit_ui` – user-facing Gemini-style search app

This mimics **real-world production** architectures and is a strong talking point in interviews.

### 🔹 Explanations

For each search result you get:

- ✅ Why this document was matched (LLM explanation)
- ✅ Which keywords overlapped (simple heuristic)
- ✅ Overlap ratio (0–1)
- ✅ Top matching sentences (semantic similarity)

---

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

### ASCII Diagram (Microservices Highlighted)

```text
                 ┌──────────────────────────┐
                 │      Streamlit UI        │
                 │  (Gemini-style frontend) │
                 └────────────┬─────────────┘
                              │ HTTP /search
                              ▼
                 ┌──────────────────────────┐
                 │      API Gateway         │  ← central orchestrator
                 └───────┬────────┬────────┘
                         │        │
                Load docs│        │Explanations
                         │        ▼
          ┌──────────────▼───┐   ┌─────────────────────┐
          │   DOC SERVICE    │   │  EXPLAIN SERVICE    │
          │ - read .txt      │   │ - keywords/overlap  │
          │ - clean + hash   │   │ - top sentences     │
          └───────────▲──────┘   │ - optional Gemini   │
                      │          └─────────▲───────────┘
                      │ Embeddings         │
          ┌───────────┴───────────┐        │
          │   EMBED SERVICE       │        │
          │ - MiniLM embeddings   │        │
          │ - caching to disk     │        │
          └───────────▲───────────┘        │
                      │ vectors            │
          ┌───────────┴───────────┐        │
          │   SEARCH SERVICE      │        │
          │ - FAISS index (L2)    │        │
          │ - Top-K search        │        │
          └───────────────────────┘        │
                                           │
          ───────── All behind API GATEWAY + Streamlit UI ─────────
