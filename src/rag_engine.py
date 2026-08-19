"""
Orquestra o fluxo completo de RAG:
  1. Recebe a pergunta do usuário.
  2. Gera o embedding da pergunta (local, sentence-transformers).
  3. Busca os chunks mais similares no índice FAISS.
  4. Envia pergunta + contexto para o modelo de chat da Groq.
  5. Retorna a resposta junto com as fontes usadas (para transparência).
"""
from dataclasses import dataclass, field
from typing import List

from src.config import TOP_K
from src.embeddings import embed_texts
from src.vector_store import VectorStore
from src.llm import generate_answer


@dataclass
class RagAnswer:
    answer: str
    sources: List[str] = field(default_factory=list)


class RagEngine:
    def __init__(self):
        self.vector_store = VectorStore()
        if not self.vector_store.load():
            raise RuntimeError(
                "Índice vetorial não encontrado. Rode 'python scripts/build_index.py' "
                "antes de iniciar o agente."
            )

    def ask(self, question: str) -> RagAnswer:
        query_embedding = embed_texts([question])[0]
        results = self.vector_store.search(query_embedding, top_k=TOP_K)

        if not results:
            return RagAnswer(
                answer="Não encontrei informações relacionadas a essa pergunta na minha base de conhecimento.",
                sources=[],
            )

        context_chunks = [chunk.text for chunk, _score in results]
        sources = sorted({chunk.source for chunk, _score in results})

        answer_text = generate_answer(question, context_chunks)
        return RagAnswer(answer=answer_text, sources=sources)
