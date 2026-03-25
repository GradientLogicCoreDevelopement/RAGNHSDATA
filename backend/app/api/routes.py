from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.ingestion import ingest_file
from app.services.rag import ask

router = APIRouter()


class IngestRequest(BaseModel):
    file_path: str
    client_id: str


class AskRequest(BaseModel):
    question: str
    client_id: str


@router.post("/ingest")
def ingest(req: IngestRequest):
    try:
        result = ingest_file(req.file_path, req.client_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/ask")
def ask_question(req: AskRequest):
    try:
        result = ask(req.question, req.client_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))