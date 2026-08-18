"""Shared configuration for the Clinical RAG pipeline."""
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()

DATA_DIR = PROJECT_ROOT / "references"
PDF_PATH = DATA_DIR / "56-364NFULL.pdf"

DOC_ID = "nhlbi-scd-2014"
DOC_TITLE = "Evidence-Based Management of Sickle Cell Disease: Expert Panel Report, 2014"
DOC_CITATION = "National Heart, Lung, and Blood Institute (2014). Evidence-Based Management of Sickle Cell Disease: Expert Panel Report, 2014."

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
TOP_K = 4

COLLECTION_NAME = "scd_clinical_kb"
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_CHAT_MODEL = os.environ.get("OPENAI_CHAT_MODEL", "gpt-4o-mini")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b")
