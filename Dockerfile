FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY scripts/ ./scripts/
COPY data/ ./data/
COPY app.py .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Constrói o índice vetorial no primeiro start (os embeddings são locais,
# não dependem de nenhuma chave de API) e depois inicia o Streamlit.
CMD ["sh", "-c", "python scripts/build_index.py && streamlit run app.py --server.port=8501 --server.address=0.0.0.0"]
