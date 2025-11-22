# src/embed_service/cache_manager.py
import os
import json
import numpy as np

CACHE_DIR = "cache"
META_PATH = f"{CACHE_DIR}/embed_meta.json"
EMB_PATH = f"{CACHE_DIR}/embeddings.npy"

class CacheManager:
    def __init__(self):
        os.makedirs(CACHE_DIR, exist_ok=True)
        if os.path.exists(META_PATH):
            with open(META_PATH, "r") as f:
                self.meta = json.load(f)
        else:
            self.meta = {}  # filename -> {"hash":..., "index": int}

        if os.path.exists(EMB_PATH):
            self.embeddings = np.load(EMB_PATH)
        else:
            # empty array shaped (0, dim) — we'll resize when first embedding arrives
            self.embeddings = np.zeros((0, 384), dtype="float32")

    def save(self):
        with open(META_PATH, "w") as f:
            json.dump(self.meta, f, indent=2)
        np.save(EMB_PATH, self.embeddings)

    def exists(self, filename: str, file_hash: str) -> bool:
        return filename in self.meta and self.meta[filename]["hash"] == file_hash

    def get_embedding(self, filename: str):
        idx = int(self.meta[filename]["index"])
        return self.embeddings[idx]

    def add_embedding(self, filename: str, file_hash: str, embedding):
        embedding = embedding.astype("float32")
        idx = len(self.embeddings)
        self.meta[filename] = {"hash": file_hash, "index": idx}
        if self.embeddings.shape[0] == 0:
            self.embeddings = embedding.reshape(1, -1)
        else:
            self.embeddings = np.vstack([self.embeddings, embedding.reshape(1, -1)])
        self.save()

    def all_embeddings(self):
        return self.meta, self.embeddings
