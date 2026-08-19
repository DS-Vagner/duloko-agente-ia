"""
Leitura e "chunking" (fragmentação) dos documentos da base de conhecimento
(PDF ou CSV). Cada chunk vira uma unidade de recuperação no índice FAISS.
"""
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import List

from pypdf import PdfReader

from src.config import CHUNK_SIZE, CHUNK_OVERLAP


@dataclass
class Chunk:
    text: str
    source: str    # nome do arquivo de origem (ex: reembolsos_e_devolucoes.pdf)
    chunk_id: int   # posição do chunk dentro do arquivo


def _split_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    """Divide um texto longo em pedaços menores com sobreposição."""
    text = " ".join(text.split())  # normaliza espaços/quebras de linha
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
        if start < 0:
            start = 0
        if end >= len(text):
            break
    return chunks


def load_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    pages_text = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages_text)


def load_csv(path: Path) -> str:
    """Converte cada linha do CSV em uma frase 'coluna: valor'."""
    rows_text = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_text = "; ".join(f"{k}: {v}" for k, v in row.items() if v)
            rows_text.append(row_text)
    return "\n".join(rows_text)


def load_documents(data_dir: Path) -> List[Chunk]:
    """Lê todos os .pdf e .csv de data_dir e retorna os chunks prontos para indexar."""
    all_chunks: List[Chunk] = []

    for path in sorted(data_dir.glob("*")):
        if path.suffix.lower() == ".pdf":
            raw_text = load_pdf(path)
        elif path.suffix.lower() == ".csv":
            raw_text = load_csv(path)
        else:
            continue

        pieces = _split_text(raw_text, CHUNK_SIZE, CHUNK_OVERLAP)
        for i, piece in enumerate(pieces):
            all_chunks.append(Chunk(text=piece, source=path.name, chunk_id=i))

    return all_chunks
