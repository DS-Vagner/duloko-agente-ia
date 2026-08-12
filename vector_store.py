"""
Índice vetorial local (FAISS) para armazenar embeddings dos chunks e
recuperar os mais relevantes para uma pergunta.

Guardamos o índice + os metadados (texto e origem de cada chunk) em disco,
para não precisar rechamar o serviço de embeddings a cada reinício da API.
"""
import pickle
from pathlib import Path
from typing import List, Tuple

import faiss
import numpy as np

from app.document_loader import Chunk
from app.config import INDEX_DIR

INDEX_PATH = INDEX_DIR / "faiss.index"
METADATA_PATH = INDEX_DIR / "metadata.pkl"


class VectorStore:
    def __init__(self):
        self.index: faiss.Index | None = None
        self.chunks: List[Chunk] = []

    def build(self, chunks: List[Chunk], embeddings: List[List[float]]) -> None:
        vectors = np.array(embeddings, dtype="float32")
        faiss.normalize_L2(vectors)  # normaliza para usar similaridade de cosseno
        dim = vectors.shape[1]
        index = faiss.IndexFlatIP(dim)  # produto interno == cosseno após normalização
        index.add(vectors)
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

    def search(self, query_embedding: List[float], top_k: int) -> List[Tuple[Chunk, float]]:
        assert self.index is not None, "Índice não carregado. Rode scripts/build_index.py primeiro."
        vector = np.array([query_embedding], dtype="float32")
        faiss.normalize_L2(vector)
        scores, indices = self.index.search(vector, top_k)
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            results.append((self.chunks[idx], float(score)))
        return results
