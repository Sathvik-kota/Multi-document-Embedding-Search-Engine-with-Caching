# src/search_service/indexer.py
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

    def try_load(self):
        if not os.path.exists(self.meta_path) or not os.path.exists(self.index_path):
            return None, None
        with open(self.meta_path, "rb") as f:
            meta = pickle.load(f)
        index = faiss.read_index(self.index_path)
        self.index = index
        self.meta = meta
        return meta, None

    def build(self, embeddings, meta):
        # embeddings: numpy array (N, dim)
        dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(embeddings)
        faiss.write_index(index, self.index_path)
        # normalize meta keys to str(index)->filename
        meta_map = {}
        for k, v in meta.items():
            meta_map[str(k)] = v
        with open(self.meta_path, "wb") as f:
            pickle.dump(meta_map, f)
        self.index = index
        self.meta = meta_map

    def search(self, query_emb, top_k):
        if self.index is None:
            raise ValueError("FAISS index is not loaded!")
        q = query_emb.reshape(1, -1).astype("float32")
        distances, ids = self.index.search(q, top_k)
        # distances shape (1, k), ids shape (1, k)
        return distances[0].tolist(), ids[0].tolist()
