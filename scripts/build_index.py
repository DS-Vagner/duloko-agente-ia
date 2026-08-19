"""
Script de ingestão: lê os documentos de data/, gera embeddings locais
(sentence-transformers) e persiste o índice vetorial (FAISS) em disco.

Uso:
    python scripts/build_index.py

Não precisa de nenhuma chave de API — os embeddings rodam localmente.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import DATA_DIR
from src.document_loader import load_documents
from src.embeddings import embed_texts
from src.vector_store import VectorStore


def main():
    print(f"Lendo documentos de: {DATA_DIR}")
    chunks = load_documents(DATA_DIR)
    print(f"{len(chunks)} chunks gerados a partir dos documentos.")

    if not chunks:
        print("Nenhum documento .pdf ou .csv encontrado em data/. Abortando.")
        return

    print("Gerando embeddings locais (sentence-transformers)... "
          "primeira execução pode demorar um pouco para baixar o modelo.")
    texts = [c.text for c in chunks]
    embeddings = embed_texts(texts)
    print(f"Embeddings gerados: {embeddings.shape}")

    print("Construindo índice vetorial (FAISS)...")
    store = VectorStore()
    store.build(chunks, embeddings)
    store.save()

    print("Índice salvo com sucesso em /index. O agente está pronto para responder perguntas.")


if __name__ == "__main__":
    main()
