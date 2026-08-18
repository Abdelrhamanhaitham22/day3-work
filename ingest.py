"""Document loading and chunking utilities."""
import re
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

import config
from query import build_index


def looks_like_toc_or_refs(text: str) -> bool:
    dot_leader_lines = len(re.findall(r"\.{4,}\s*\d+", text))
    return dot_leader_lines >= 2


def load_pdfs(data_dir: Path | None = None) -> list:
    if data_dir is None:
        data_dir = config.DATA_DIR
    pdf_path = data_dir / "56-364NFULL.pdf"
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found at {pdf_path}")

    loader = PyPDFLoader(str(pdf_path))
    pages = loader.load()

    for page in pages:
        page.metadata.update({
            "document_id": config.DOC_ID,
            "title": config.DOC_TITLE,
            "citation": config.DOC_CITATION,
            "page_number": page.metadata.get("page", 0) + 1,
        })

    pages = [p for p in pages if not looks_like_toc_or_refs(p.page_content)]
    return pages


def chunk_documents(
    pages: list,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list:
    if chunk_size is None:
        chunk_size = config.CHUNK_SIZE
    if chunk_overlap is None:
        chunk_overlap = config.CHUNK_OVERLAP

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(pages)

    counters = {}
    for chunk in chunks:
        doc_id = chunk.metadata.get("document_id", "doc")
        counters[doc_id] = counters.get(doc_id, 0) + 1
        chunk.metadata["chunk_id"] = f"{doc_id}-CH-{counters[doc_id]:04d}"

    return chunks
