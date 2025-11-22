# cache_manager.py
import os
import json
import numpy as np

CACHE_DIR = "cache"
META_PATH = f"{CACHE_DIR}/embed_meta.json"
EMB_PATH = f"{CACHE_DIR}/embeddings.npy"

class CacheManager:
    def __init__(self):
        os.makedirs(CACHE_DIR, exist_ok=True)

        # Load metadata
        if os.path.exists(META_PATH):
            with open(META_PATH, "r") as f:
                self.meta = json.load(f)
        else:
            self.meta = {}   # {filename: {hash, index}}

        # Load embeddings file
        if os.path.exists(EMB_PATH):
            self.embeddings = np.load(EMB_PATH)
        else:
            self.embeddings = np.zeros((0, 384), dtype="float32")  # 384 dim for MiniLM

    def save(self):
        """Persist metadata + embeddings to disk."""
        with open(META_PATH, "w") as f:
            json.dump(self.meta, f, indent=2)
        np.save(EMB_PATH, self.embeddings)

    def exists(self, filename: str, file_hash: str):
        """Check if file already embedded and unchanged."""
        return filename in self.meta and self.meta[filename]["hash"] == file_hash

    def get_embedding(self, filename: str):
        """Return embedding for an already cached file."""
        idx = self.meta[filename]["index"]
        return self.embeddings[idx]

    def add_embedding(self, filename: str, file_hash: str, embedding: np.ndarray):
        """Add a new embedding to cache."""
        idx = len(self.embeddings)
        self.meta[filename] = {
            "hash": file_hash,
            "index": idx
        }

        # Append embedding
        if len(self.embeddings) == 0:
            self.embeddings = embedding.reshape(1, -1)
        else:
            self.embeddings = np.vstack([self.embeddings, embedding])

        self.save()

    def all_embeddings(self):
        """Return all embeddings + mapping."""
        return self.meta, self.embeddings
