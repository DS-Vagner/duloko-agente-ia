FROM python:3.11-slim

WORKDIR /app

# Dependências de sistema necessárias para faiss-cpu / pypdf
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY scripts/ ./scripts/
COPY data/ ./data/

EXPOSE 8000

# Constrói o índice no build (assume que as credenciais OCI serão fornecidas
# em runtime via variáveis de ambiente / instance principal na OCI).
# Caso prefira, comente a linha abaixo e rode build_index.py manualmente
# antes do deploy, versionando a pasta index/.
CMD ["sh", "-c", "python scripts/build_index.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
