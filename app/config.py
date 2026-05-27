import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.environ["GROQ_API_KEY"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
JINA_API_KEY = os.environ["JINA_API_KEY"]

CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")
BM25_INDEX_PATH = os.getenv("BM25_INDEX_PATH", "./data/bm25_index.pkl")
BIBLE_DATA_PATH = os.getenv("BIBLE_DATA_PATH", "./data/bibles")
DENOM_DATA_PATH = os.getenv("DENOM_DATA_PATH", "./data/denominations")
HISTORICAL_FACTS_PATH = os.getenv("HISTORICAL_FACTS_PATH", "./data/historical_facts.json")

MAX_REGEN_ATTEMPTS = int(os.getenv("MAX_REGEN_ATTEMPTS", "2"))
MEMORY_WINDOW_SIZE = int(os.getenv("MEMORY_WINDOW_SIZE", "6"))
BM25_TOP_K = int(os.getenv("BM25_TOP_K", "5"))
DENSE_TOP_K = int(os.getenv("DENSE_TOP_K", "5"))
FUSED_TOP_K = int(os.getenv("FUSED_TOP_K", "3"))

GROQ_PRIMARY_MODEL = "llama-3.3-70b-versatile"
GROQ_FAST_MODEL = "llama-3.1-8b-instant"
GROQ_VISION_MODEL = "llama-3.2-90b-vision-preview"
GROQ_GUARD_MODEL = "llama-guard-4-12b"
GEMINI_IMAGE_MODEL = "gemini-2.0-flash-exp"
JINA_EMBED_MODEL = "jina-embeddings-v3"
JINA_EMBED_DIM = 1024
