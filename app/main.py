"""FastAPI entry point. Stub — implemented in Phase 8."""
from fastapi import FastAPI

app = FastAPI(title="Christianity AI Assistant")


@app.get("/health")
def health():
    return {"status": "ok"}
