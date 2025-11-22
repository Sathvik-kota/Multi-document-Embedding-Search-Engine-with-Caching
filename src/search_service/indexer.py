# indexer.py
import os
import faiss
import numpy as np
import json

INDEX_DIR = "cache"
INDEX_PATH = f"{INDEX_DIR}/faiss_index.bin"
META_PATH = f"{INDEX_DIR}/faiss_meta.json"


class FAISSIndexer:
    def __init__(self, dim=384):
        self.dim = dim
        self.index = None
        os.makedirs(INDEX_DIR, exist_ok=True)

    # Normalize vectors for cosine similarity
    def _normalize(self, x):
        norm = np.linalg.norm(x, axis=1, keepdims=True) + 1e-10
        return x / norm

    def build(self, embeddings: np.ndarray, meta: dict):
        """Build FAISS index from embeddings."""
        if embeddings.shape[0] == 0:
            print("⚠️ No embeddings found — index is empty.")
            return

        emb_norm = self._normalize(embeddings)
        index = faiss.IndexFlatIP(self.dim)
        index.add(emb_norm)

        self.index = index

        # Save meta (filename to index position)
        with open(META_PATH, "w") as f:
            json.dump(meta, f, indent=2)

        # Save FAISS index
        faiss.write_index(index, INDEX_PATH)

        print("✅ FAISS index built and saved.")

    def load(self):
        """Load FAISS index + metadata."""
        if os.path.exists(INDEX_PATH):
            self.index = faiss.read_index(INDEX_PATH)
            print("🔄 Loaded FAISS index.")
        else:
            print("⚠️ No saved index found.")

        if os.path.exists(META_PATH):
            with open(META_PATH, "r") as f:
                meta = json.load(f)
            print("🔄 Loaded FAISS metadata.")
        else:
            meta = {}

        return meta

    def search(self, query_emb: np.ndarray, top_k: int):
        """Search top-K similar documents."""
        if self.index is None:
            raise ValueError("FAISS index is not loaded!")

        # Normalize query
        q = query_emb.reshape(1, -1)
        q = q / (np.linalg.norm(q) + 1e-10)

        scores, ids = self.index.search(q, top_k)

        return scores[0], ids[0]
