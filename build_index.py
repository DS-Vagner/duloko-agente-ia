"""
Script de ingestão: lê os documentos de data/, gera embeddings via OCI
Generative AI e persiste o índice vetorial (FAISS) em disco.

Uso:
    python scripts/build_index.py
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.config import DATA_DIR
from app.document_loader import load_documents
from app.oci_genai_client import OCIGenAIClient
from app.vector_store import VectorStore


def main():
    print(f"Lendo documentos de: {DATA_DIR}")
    chunks = load_documents(DATA_DIR)
    print(f"{len(chunks)} chunks gerados a partir dos documentos.")

    if not chunks:
        print("Nenhum documento .pdf ou .csv encontrado em data/. Abortando.")
        return

    print("Gerando embeddings via OCI Generative AI...")
    client = OCIGenAIClient()

    # Gera embeddings em lotes para não estourar limites da API
    batch_size = 96
    all_embeddings = []
    for i in range(0, len(chunks), batch_size):
        batch = [c.text for c in chunks[i : i + batch_size]]
        embeddings = client.embed_texts(batch)
        all_embeddings.extend(embeddings)
        print(f"  Embeddings gerados: {len(all_embeddings)}/{len(chunks)}")

    print("Construindo índice vetorial (FAISS)...")
    store = VectorStore()
    store.build(chunks, all_embeddings)
    store.save()

    print("Índice salvo com sucesso em /index. Pronto para iniciar a API.")


if __name__ == "__main__":
    main()
