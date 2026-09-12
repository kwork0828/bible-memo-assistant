from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, status

from backend.firebase_client import get_firestore_client
from backend.models import ConversationCreate, ConversationResponse


router = APIRouter(prefix="/api/conversations", tags=["conversations"])
COLLECTION_NAME = "conversations"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _get_collection():
    try:
        db = get_firestore_client()
        return db.collection(COLLECTION_NAME)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firestore 연결에 실패했습니다. 서버 설정을 확인하세요.",
        ) from error


def _snapshot_to_response(snapshot) -> dict[str, Any]:
    data = snapshot.to_dict() or {}
    return {"id": snapshot.id, **data}


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(payload: ConversationCreate):
    collection = _get_collection()
    document = collection.document()
    now = _utc_now_iso()
    document_data = {
        **payload.model_dump(),
        "created_at": now,
        "updated_at": now,
    }
    document.set(document_data)
    return {"id": document.id, **document_data}


@router.get("", response_model=list[ConversationResponse])
def list_conversations():
    collection = _get_collection()
    snapshots = collection.order_by("updated_at", direction="DESCENDING").stream()
    return [_snapshot_to_response(snapshot) for snapshot in snapshots]


@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(conversation_id: str):
    collection = _get_collection()
    snapshot = collection.document(conversation_id).get()

    if not snapshot.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="대화를 찾을 수 없습니다.",
        )

    return _snapshot_to_response(snapshot)


@router.delete("/{conversation_id}")
def delete_conversation(conversation_id: str):
    collection = _get_collection()
    document = collection.document(conversation_id)
    snapshot = document.get()

    if not snapshot.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="삭제할 대화를 찾을 수 없습니다.",
        )

    document.delete()
    return {"status": "deleted", "id": conversation_id}
