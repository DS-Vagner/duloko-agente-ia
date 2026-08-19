"""
Testes automatizados do Agente DuLoko.

Os testes de leitura/chunking rodam de verdade (não dependem de API).
O teste do RagEngine usa mock, já que chamar a Groq de verdade requer
GROQ_API_KEY configurada (não deve rodar em CI sem ela).
"""
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.document_loader import load_documents, _split_text
from src.config import DATA_DIR
from src.rag_engine import RagAnswer


def test_split_text_respeita_tamanho_aproximado():
    texto = "palavra " * 500  # texto longo o suficiente para gerar múltiplos chunks
    chunks = _split_text(texto, chunk_size=100, overlap=20)
    assert len(chunks) > 1
    assert all(len(c) <= 100 for c in chunks)


def test_load_documents_le_pdfs_reais():
    chunks = load_documents(DATA_DIR)
    assert len(chunks) > 0
    fontes = {c.source for c in chunks}
    # confirma que os 5 documentos da DuLoko foram processados
    assert "reembolsos_e_devolucoes.pdf" in fontes
    assert "garantia_de_produtos.pdf" in fontes
    assert "metodos_de_pagamento.pdf" in fontes
    assert "prazos_e_custos_de_envio.pdf" in fontes
    assert "programa_de_afiliacao.pdf" in fontes


@patch("src.rag_engine.RagEngine.__init__", return_value=None)
def test_rag_answer_dataclass(mock_init):
    resposta = RagAnswer(
        answer="Você pode devolver o produto em até 10 dias corridos.",
        sources=["reembolsos_e_devolucoes.pdf"],
    )
    assert "10 dias" in resposta.answer
    assert "reembolsos_e_devolucoes.pdf" in resposta.sources
