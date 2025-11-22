# search_service/indexer.py

import numpy as np
import faiss
import os
import pickle

class FAISSIndexer:
    def __init__(self):
        self.index = None
        self.meta = None
        self.index_path = "faiss_index.bin"
        self.meta_path = "faiss_meta.pkl"

    # ----------------------------------------
    # Load cache (embeddings + meta)
    # ----------------------------------------
    def try_load(self):
        if not os.path.exists(self.meta_path) or not os.path.exists(self.index_path):
            return None, None

        with open(self.meta_path, "rb") as f:
            meta = pickle.load(f)

        index = faiss.read_index(self.index_path)

        # Extract embeddings back from FAISS index
        xb = faiss.vector_to_array(index.xb).reshape(-1, index.d)

        self.index = index
        self.meta = meta

        return meta, xb

    # ----------------------------------------
    # Build FAISS index from embeddings
    # ----------------------------------------
    def build(self, embeddings, meta):
        dim = embeddings.shape[1]

        index = faiss.IndexFlatL2(dim)
        index.add(embeddings)

        # Save index + metadata
        faiss.write_index(index, self.index_path)

        with open(self.meta_path, "wb") as f:
            pickle.dump(meta, f)

        self.index = index
        self.meta = meta

    # ----------------------------------------
    # Search
    # ----------------------------------------
    def search(self, query_emb, top_k):
        if self.index is None:
            raise ValueError("FAISS index is not loaded!")

        scores, ids = self.index.search(query_emb, top_k)
        return scores, ids
