from typing import Literal
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from utils.privacy_guard import ensure_non_sensitive
from services.ollama_service import ask_ollama

router = APIRouter(prefix="/api/v1/ai", tags=["AI assistant"])


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1500)
    history: list[dict] = Field(default_factory=list, max_length=8)


class ChatResponse(BaseModel):
    answer: str
    privacy: Literal["input screened; not sent if sensitive"] = "input screened; not sent if sensitive"


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        ensure_non_sensitive(request.message)
        # Screen prior user messages too; do not forward untrusted history containing identifiers.
        safe_history = []
        for item in request.history:
            content = item.get("content", "") if isinstance(item, dict) else ""
            role = item.get("role") if isinstance(item, dict) else None
            if role in {"user", "assistant"} and isinstance(content, str):
                ensure_non_sensitive(content)
                safe_history.append({"role": role, "content": content[:1500]})
        answer = await ask_ollama(request.message, safe_history)
        return ChatResponse(answer=answer)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
