"""
Configurações centrais da aplicação.

Todos os valores sensíveis (OCIDs, endpoints) vêm de variáveis de ambiente,
carregadas a partir de um arquivo .env na raiz do projeto (veja .env.example).
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# --- OCI ---------------------------------------------------------------
OCI_CONFIG_PROFILE = os.getenv("OCI_CONFIG_PROFILE", "DEFAULT")
OCI_COMPARTMENT_ID = os.getenv("OCI_COMPARTMENT_ID", "")
OCI_GENAI_ENDPOINT = os.getenv(
    "OCI_GENAI_ENDPOINT",
    "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com",
)
EMBED_MODEL_ID = os.getenv("EMBED_MODEL_ID", "cohere.embed-multilingual-v3.0")
CHAT_MODEL_ID = os.getenv("CHAT_MODEL_ID", "meta.llama-3.1-70b-instruct")

# --- RAG -----------------------------------------------------------------
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data"))
INDEX_DIR = Path(os.getenv("INDEX_DIR", BASE_DIR / "index"))
INDEX_DIR.mkdir(parents=True, exist_ok=True)

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))       # caracteres por chunk
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "120"))  # sobreposição entre chunks
TOP_K = int(os.getenv("TOP_K", "4"))                    # nº de chunks recuperados por pergunta
