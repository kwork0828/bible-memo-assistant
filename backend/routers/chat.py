import json
import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, status

from backend.firebase_client import get_firestore_client
from backend.models import ChatRequest, ChatResponse
from backend.services.openai_client import create_chat_reply
from backend.services.summary import build_data_summary


router = APIRouter(prefix="/api/chat", tags=["chat"])
logger = logging.getLogger(__name__)
MAX_HISTORY_MESSAGES = 20


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _get_db():
    try:
        return get_firestore_client()
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firestore 연결에 실패했습니다. 서버 설정을 확인하세요.",
        ) from error


def _build_system_prompt(data_summary: dict[str, Any]) -> str:
    summary_json = json.dumps(data_summary, ensure_ascii=False)
    return (
        "너는 영어성경 암송 일정을 돕는 AI 비서다. "
        "사용자의 실제 암송 데이터 요약을 근거로 답하고, 데이터에 없는 사실은 추측하지 않는다. "
        "필요하면 모른다고 말하고 사용자가 확인할 다음 행동을 제안한다. "
        f"현재 암송 데이터 요약: {summary_json}"
    )


def _normalize_history(messages: list[dict[str, Any]]) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    for message in messages[-MAX_HISTORY_MESSAGES:]:
        role = message.get("role")
        content = message.get("content")
        if role in {"user", "assistant"} and isinstance(content, str) and content.strip():
            normalized.append({"role": role, "content": content.strip()})
    return normalized


@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest):
    db = _get_db()
    data_records = [snapshot.to_dict() or {} for snapshot in db.collection("data").stream()]
    data_summary = build_data_summary(data_records)

    conversations = db.collection("conversations")
    existing_messages: list[dict[str, Any]] = []
    conversation_document = None
    conversation_data: dict[str, Any] = {}

    if payload.conversation_id:
        conversation_document = conversations.document(payload.conversation_id)
        snapshot = conversation_document.get()
        if not snapshot.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="대화를 찾을 수 없습니다.",
            )
        conversation_data = snapshot.to_dict() or {}
        existing_messages = conversation_data.get("messages", [])

    history = _normalize_history(existing_messages)
    api_messages = [
        {"role": "system", "content": _build_system_prompt(data_summary)},
        *history,
        {"role": "user", "content": payload.message},
    ]

    try:
        reply = create_chat_reply(api_messages)
    except Exception as error:
        logger.exception("AI chat request failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI 응답 생성에 실패했습니다. API 설정과 모델을 확인하세요.",
        ) from error

    now = _utc_now_iso()
    saved_messages = [
        *existing_messages,
        {"role": "user", "content": payload.message},
        {"role": "assistant", "content": reply},
    ]

    if conversation_document is None:
        conversation_document = conversations.document()
        conversation_data = {
            "title": payload.message.strip()[:40] or "새 대화",
            "created_at": now,
        }

    conversation_document.set(
        {
            "title": conversation_data.get("title", "새 대화"),
            "messages": saved_messages,
            "created_at": conversation_data.get("created_at", now),
            "updated_at": now,
        },
        merge=True,
    )

    return {
        "conversation_id": conversation_document.id,
        "reply": reply,
        "data_summary": data_summary,
    }
