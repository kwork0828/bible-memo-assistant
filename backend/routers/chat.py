"""암송 데이터 요약을 주입한 AI 채팅 API를 제공한다."""

import json
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

from backend.firebase_client import get_firestore_client
from backend.models import ChatRequest
from backend.services.openai_client import generate_chat_reply
from backend.services.summary import build_data_summary


router = APIRouter(prefix="/api/chat", tags=["chat"])
DATA_COLLECTION = "data"
CONVERSATION_COLLECTION = "conversations"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _firestore_unavailable(error: Exception) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Firestore에 연결할 수 없습니다. 서버의 Firebase 설정을 확인해주세요.",
    )


def _load_summary(db) -> dict:
    items = []
    for snapshot in db.collection(DATA_COLLECTION).stream():
        data = snapshot.to_dict() or {}
        items.append({"id": snapshot.id, **data})
    return build_data_summary(items)


def _build_system_prompt(summary: dict) -> str:
    summary_json = json.dumps(summary, ensure_ascii=False)
    return (
        "너는 영어성경 암송 학습을 돕는 AI 비서다. "
        "사용자의 실제 암송 일정 요약만 근거로 답하고, 모르는 정보는 추측하지 않는다. "
        "응답은 반드시 JSON 객체 한 개로만 반환한다. 형식은 {\"reply\": \"사용자에게 보여줄 답변\"} 이다. "
        "thought, thinking, reasoning, analysis 같은 내부 사고 필드는 절대 포함하지 않는다. "
        f"현재 암송 데이터 요약: {summary_json}"
    )


def _load_history(db, conversation_id: str) -> tuple[object, list[dict[str, str]]]:
    document = db.collection(CONVERSATION_COLLECTION).document(conversation_id)
    snapshot = document.get()
    if not snapshot.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 대화를 찾을 수 없습니다.",
        )

    data = snapshot.to_dict() or {}
    raw_messages = data.get("messages", [])
    history = [
        {"role": item.get("role", "user"), "content": str(item.get("content", ""))}
        for item in raw_messages
        if isinstance(item, dict)
        and item.get("role") in {"user", "assistant"}
        and str(item.get("content", "")).strip()
    ]
    return document, history


@router.post("")
def chat(payload: ChatRequest):
    """데이터 요약을 AI에 전달하고 답변을 대화 기록과 함께 저장한다."""
    try:
        db = get_firestore_client()
        summary = _load_summary(db)
    except HTTPException:
        raise
    except Exception as error:
        raise _firestore_unavailable(error) from error

    conversation_document = None
    history: list[dict[str, str]] = []
    if payload.conversation_id:
        try:
            conversation_document, history = _load_history(db, payload.conversation_id)
        except HTTPException:
            raise
        except Exception as error:
            raise _firestore_unavailable(error) from error

    ai_messages = [*history, {"role": "user", "content": payload.message}]

    try:
        reply = generate_chat_reply(_build_system_prompt(summary), ai_messages)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI 응답을 생성하지 못했습니다. 서버의 AI 설정과 모델 호환성을 확인해주세요.",
        ) from error

    user_message = {"role": "user", "content": payload.message}
    assistant_message = {"role": "assistant", "content": reply}
    updated_messages = [*history, user_message, assistant_message]
    now = _now_iso()

    try:
        if conversation_document is None:
            conversation_document = db.collection(CONVERSATION_COLLECTION).document()
            conversation_document.set(
                {
                    "title": payload.message.strip()[:60] or "새 대화",
                    "messages": updated_messages,
                    "created_at": now,
                    "updated_at": now,
                }
            )
        else:
            conversation_document.update(
                {
                    "messages": updated_messages,
                    "updated_at": now,
                }
            )
    except Exception as error:
        raise _firestore_unavailable(error) from error

    return {
        "conversation_id": conversation_document.id,
        "reply": reply,
        "summary": summary,
    }
