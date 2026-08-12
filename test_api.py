"""
Testes básicos da API.

O teste de /health não depende de credenciais OCI.
O teste de /ask é ilustrativo e usa mock do RagEngine, já que chamar a OCI de
verdade requer credenciais configuradas (não deve rodar em CI sem elas).
"""
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.rag_engine import RagAnswer

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch("app.main.get_engine")
def test_ask_mocked(mock_get_engine):
    mock_engine = mock_get_engine.return_value
    mock_engine.ask.return_value = RagAnswer(
        answer="Você pode devolver o produto em até 7 dias corridos após o recebimento.",
        sources=["Politica_Reembolso_Devolucoes_NovaShop.pdf"],
    )

    response = client.post("/ask", json={"question": "Qual o prazo para devolução?"})

    assert response.status_code == 200
    data = response.json()
    assert "7 dias" in data["answer"]
    assert "Politica_Reembolso_Devolucoes_NovaShop.pdf" in data["sources"]


def test_ask_pergunta_muito_curta():
    response = client.post("/ask", json={"question": "?"})
    assert response.status_code == 422  # validação do Pydantic (min_length=3)
