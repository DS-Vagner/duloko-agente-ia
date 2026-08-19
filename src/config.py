"""
Configurações centrais do Agente DuLoko.

Os valores vêm de variáveis de ambiente (arquivo .env local, ou "Secrets"
quando publicado no Streamlit Community Cloud / variáveis de ambiente da VM).
"""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Groq (LLM de geração) ---------------------------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# --- Embeddings locais (sentence-transformers) --------------------------
# Modelo multilíngue leve, roda em CPU sem custo e sem chave de API.
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "paraphrase-multilingual-MiniLM-L12-v2")

# --- RAG ------------------------------------------------------------------
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data"))
INDEX_DIR = Path(os.getenv("INDEX_DIR", BASE_DIR / "index"))
INDEX_DIR.mkdir(parents=True, exist_ok=True)

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "900"))        # caracteres por chunk
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))  # sobreposição entre chunks
TOP_K = int(os.getenv("TOP_K", "5"))                     # nº de chunks recuperados por pergunta

# --- Identidade do agente -------------------------------------------------
NOME_LOJA = "DuLoko"
NOME_AGENTE = "Assistente DuLoko"
