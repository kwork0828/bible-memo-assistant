"""Firestore conversations 컬렉션을 다루는 API 라우터."""

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

from backend.firebase_client import get_firestore_client
from backend.models import ConversationCreate, ConversationResponse


router = APIRouter(prefix="/api/conversations", tags=["conversations"])


def _document_to_response(document) -> ConversationResponse:
    payload = document.to_dict() or {}
    created_at = payload.get("created_at") or datetime.now(timezone.utc)
    if isinstance(created_at, str):
        created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    return ConversationResponse(
        id=document.id,
        title=str(payload.get("title", "암송 회고")),
        messages=payload.get("messages", []),
        god_reflection=str(payload.get("god_reflection", "")),
        today_application=str(payload.get("today_application", "")),
        yesterday_application=str(payload.get("yesterday_application", "")),
        created_at=created_at,
    )


def _get_document_reference(document_id: str):
    if not document_id or "/" in document_id:
        raise HTTPException(status_code=400, detail="유효하지 않은 대화 ID입니다.")
    return get_firestore_client().collection("conversations").document(document_id)


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(item: ConversationCreate):
    """AI 대화와 암송 후 회고를 저장한다."""
    created_at = datetime.now(timezone.utc)
    document_reference = get_firestore_client().collection("conversations").document()
    payload = item.model_dump()
    payload["created_at"] = created_at.isoformat()
    document_reference.set(payload)
    return ConversationResponse(id=document_reference.id, created_at=created_at, **item.model_dump())


@router.get("", response_model=list[ConversationResponse])
def list_conversations():
    """최근 대화부터 목록을 반환한다."""
    documents = get_firestore_client().collection("conversations").stream()
    items = [_document_to_response(document) for document in documents]
    return sorted(items, key=lambda item: item.created_at, reverse=True)


@router.get("/{document_id}", response_model=ConversationResponse)
def get_conversation(document_id: str):
    """대화 하나를 불러온다."""
    document_reference = _get_document_reference(document_id)
    snapshot = document_reference.get()
    if not snapshot.exists:
        raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다.")
    return _document_to_response(snapshot)


@router.delete("/{document_id}")
def delete_conversation(document_id: str):
    """대화 하나를 삭제한다."""
    document_reference = _get_document_reference(document_id)
    if not document_reference.get().exists:
        raise HTTPException(status_code=404, detail="대화를 찾을 수 없습니다.")
    document_reference.delete()
    return {"id": document_id, "deleted": True}
