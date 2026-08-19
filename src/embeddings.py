"""
Geração de embeddings 100% local, via sentence-transformers.

Vantagem para este projeto: não depende de nenhuma API externa nem de chave
paga — só usa CPU. O modelo é baixado uma vez (na primeira execução) e fica
em cache local.
"""
from functools import lru_cache
from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer

from src.config import EMBEDDING_MODEL


@lru_cache(maxsize=1)
def get_embedder() -> SentenceTransformer:
    """Carrega o modelo de embeddings uma única vez (cache em memória)."""
    return SentenceTransformer(EMBEDDING_MODEL)


def embed_texts(texts: List[str]) -> np.ndarray:
    """Gera embeddings normalizados (prontos para similaridade de cosseno)."""
    model = get_embedder()
    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return embeddings.astype("float32")
