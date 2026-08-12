"""
API do agente inteligente (FastAPI).

Endpoints:
  GET  /health        -> verificação simples de que a API está no ar
  POST /ask            -> recebe uma pergunta e retorna a resposta gerada pelo agente

Para rodar localmente:
  uvicorn app.main:app --reload --port 8000
"""
import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.rag_engine import RagEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agente-rag")

app = FastAPI(
    title="Agente Inteligente - NovaShop",
    description="Agente de IA (RAG) que responde perguntas com base em documentos de suporte da NovaShop.",
    version="1.0.0",
)

_engine: RagEngine | None = None


def get_engine() -> RagEngine:
    global _engine
    if _engine is None:
        _engine = RagEngine()
    return _engine


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, examples=["Qual o prazo para devolver um produto?"])


class AskResponse(BaseModel):
    answer: str
    sources: list[str]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    try:
        engine = get_engine()
        result = engine.ask(request.question)
        return AskResponse(answer=result.answer, sources=result.sources)
    except RuntimeError as e:
        # índice não construído ainda
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.exception("Erro ao processar pergunta")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")
