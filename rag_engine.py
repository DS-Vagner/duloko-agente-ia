"""
Orquestra o fluxo completo de RAG:
  1. Recebe a pergunta do usuário.
  2. Gera o embedding da pergunta.
  3. Busca os chunks mais similares no índice vetorial.
  4. Envia pergunta + contexto para o modelo de chat da OCI.
  5. Retorna a resposta junto com as fontes usadas (para transparência).
"""
from dataclasses import dataclass, field
from typing import List

from app.config import TOP_K
from app.oci_genai_client import OCIGenAIClient
from app.vector_store import VectorStore


@dataclass
class RagAnswer:
    answer: str
    sources: List[str] = field(default_factory=list)


class RagEngine:
    def __init__(self):
        self.genai_client = OCIGenAIClient()
        self.vector_store = VectorStore()
        if not self.vector_store.load():
            raise RuntimeError(
                "Índice vetorial não encontrado. Rode 'python scripts/build_index.py' "
                "antes de iniciar a API."
            )

    def ask(self, question: str) -> RagAnswer:
        query_embedding = self.genai_client.embed_texts([question])[0]
        results = self.vector_store.search(query_embedding, top_k=TOP_K)

        if not results:
            return RagAnswer(
                answer="Não encontrei informações relacionadas a essa pergunta na minha base de conhecimento.",
                sources=[],
            )

        context_chunks = [chunk.text for chunk, _score in results]
        sources = sorted({chunk.source for chunk, _score in results})

        answer_text = self.genai_client.chat(question, context_chunks)
        return RagAnswer(answer=answer_text, sources=sources)
