"""
Índice vetorial local (FAISS) para armazenar embeddings dos chunks e
recuperar os mais relevantes para uma pergunta.
"""
import pickle
from typing import List, Tuple

import faiss
import numpy as np

from src.document_loader import Chunk
from src.config import INDEX_DIR

INDEX_PATH = INDEX_DIR / "faiss.index"
METADATA_PATH = INDEX_DIR / "metadata.pkl"


class VectorStore:
    def __init__(self):
        self.index = None
        self.chunks: List[Chunk] = []

    def build(self, chunks: List[Chunk], embeddings: np.ndarray) -> None:
        dim = embeddings.shape[1]
        index = faiss.IndexFlatIP(dim)  # produto interno == cosseno (embeddings já normalizados)
        index.add(embeddings)
        self.index = index
        self.chunks = chunks

    def save(self) -> None:
        assert self.index is not None, "Índice ainda não foi construído."
        faiss.write_index(self.index, str(INDEX_PATH))
        with open(METADATA_PATH, "wb") as f:
            pickle.dump(self.chunks, f)

    def load(self) -> bool:
        if not INDEX_PATH.exists() or not METADATA_PATH.exists():
            return False
        self.index = faiss.read_index(str(INDEX_PATH))
        with open(METADATA_PATH, "rb") as f:
            self.chunks = pickle.load(f)
        return True

    def search(self, query_embedding: np.ndarray, top_k: int) -> List[Tuple[Chunk, float]]:
        assert self.index is not None, "Índice não carregado."
        vector = query_embedding.reshape(1, -1)
        scores, indices = self.index.search(vector, top_k)
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            results.append((self.chunks[idx], float(score)))
        return results
