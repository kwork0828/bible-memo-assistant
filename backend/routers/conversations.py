"""Firestore conversations 컬렉션의 저장·조회·삭제 API를 제공한다."""

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

from backend.firebase_client import get_firestore_client
from backend.models import ConversationCreate


router = APIRouter(prefix="/api/conversations", tags=["conversations"])
COLLECTION_NAME = "conversations"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _snapshot_to_dict(snapshot) -> dict:
    data = snapshot.to_dict() or {}
    return {"id": snapshot.id, **data}


def _firestore_unavailable(error: Exception) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Firestore에 연결할 수 없습니다. 서버의 Firebase 설정을 확인해주세요.",
    )


@router.post("", status_code=status.HTTP_201_CREATED)
def create_conversation(payload: ConversationCreate):
    """새 대화 문서를 저장한다."""
    try:
        db = get_firestore_client()
        document = db.collection(COLLECTION_NAME).document()
        now = _now_iso()
        data = {
            "title": payload.title,
            "messages": [message.model_dump() for message in payload.messages],
            "created_at": now,
            "updated_at": now,
        }
        document.set(data)
        return {"id": document.id, **data}
    except Exception as error:
        raise _firestore_unavailable(error) from error


@router.get("")
def list_conversations():
    """대화 목록을 최근 수정 순으로 반환한다."""
    try:
        db = get_firestore_client()
        items = [
            _snapshot_to_dict(snapshot)
            for snapshot in db.collection(COLLECTION_NAME).stream()
        ]
    except Exception as error:
        raise _firestore_unavailable(error) from error

    items.sort(key=lambda item: str(item.get("updated_at", "")), reverse=True)
    return {"items": items, "count": len(items)}


@router.get("/{conversation_id}")
def get_conversation(conversation_id: str):
    """대화 ID 하나를 조회한다."""
    try:
        db = get_firestore_client()
        snapshot = db.collection(COLLECTION_NAME).document(conversation_id).get()
        if not snapshot.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 대화를 찾을 수 없습니다.",
            )
        return _snapshot_to_dict(snapshot)
    except HTTPException:
        raise
    except Exception as error:
        raise _firestore_unavailable(error) from error


@router.delete("/{conversation_id}")
def delete_conversation(conversation_id: str):
    """지정한 대화 문서를 삭제한다."""
    try:
        db = get_firestore_client()
        document = db.collection(COLLECTION_NAME).document(conversation_id)
        snapshot = document.get()
        if not snapshot.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 대화를 찾을 수 없습니다.",
            )
        document.delete()
        return {"id": conversation_id, "deleted": True}
    except HTTPException:
        raise
    except Exception as error:
        raise _firestore_unavailable(error) from error
