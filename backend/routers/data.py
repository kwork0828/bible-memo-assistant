"""Firestore data 컬렉션의 CRUD와 요약 API를 제공한다."""

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

from backend.firebase_client import get_firestore_client
from backend.models import DataCreate, DataUpdate
from backend.services.summary import build_data_summary


router = APIRouter(prefix="/api/data", tags=["data"])
COLLECTION_NAME = "data"


def _now_iso() -> str:
    """서버 기록용 UTC 시각을 ISO 문자열로 만든다."""
    return datetime.now(timezone.utc).isoformat()


def _snapshot_to_dict(snapshot) -> dict:
    """Firestore 문서를 API 응답용 dict로 변환한다."""
    data = snapshot.to_dict() or {}
    return {"id": snapshot.id, **data}


def _firestore_unavailable(error: Exception) -> HTTPException:
    """내부 인증 정보는 숨기고 사용자에게 연결 문제만 알린다."""
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Firestore에 연결할 수 없습니다. 서버의 Firebase 설정을 확인해주세요.",
    )


@router.post("", status_code=status.HTTP_201_CREATED)
def create_data(payload: DataCreate):
    """하루 암송 일정 문서를 새로 저장한다."""
    try:
        db = get_firestore_client()
        document = db.collection(COLLECTION_NAME).document()
        now = _now_iso()
        data = {
            **payload.model_dump(),
            "created_at": now,
            "updated_at": now,
        }
        document.set(data)
        return {"id": document.id, **data}
    except Exception as error:
        raise _firestore_unavailable(error) from error


@router.get("")
def list_data():
    """저장된 암송 일정을 날짜 순서로 반환한다."""
    try:
        db = get_firestore_client()
        items = [
            _snapshot_to_dict(snapshot)
            for snapshot in db.collection(COLLECTION_NAME).stream()
        ]
    except Exception as error:
        raise _firestore_unavailable(error) from error

    items.sort(key=lambda item: str(item.get("date", "")))
    return {"items": items, "count": len(items)}


@router.get("/summary")
def get_data_summary():
    """AI 컨텍스트와 화면 표시용 간단 통계를 반환한다."""
    try:
        db = get_firestore_client()
        items = [
            _snapshot_to_dict(snapshot)
            for snapshot in db.collection(COLLECTION_NAME).stream()
        ]
    except Exception as error:
        raise _firestore_unavailable(error) from error

    return build_data_summary(items)


@router.put("/{item_id}")
def update_data(item_id: str, payload: DataUpdate):
    """지정한 data 문서의 전달된 필드만 수정한다."""
    changes = payload.model_dump(exclude_none=True)
    if not changes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="수정할 값을 하나 이상 보내주세요.",
        )

    try:
        db = get_firestore_client()
        document = db.collection(COLLECTION_NAME).document(item_id)
        snapshot = document.get()
        if not snapshot.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 data 문서를 찾을 수 없습니다.",
            )

        changes["updated_at"] = _now_iso()
        document.update(changes)
        return _snapshot_to_dict(document.get())
    except HTTPException:
        raise
    except Exception as error:
        raise _firestore_unavailable(error) from error


@router.delete("/{item_id}")
def delete_data(item_id: str):
    """지정한 data 문서를 삭제한다."""
    try:
        db = get_firestore_client()
        document = db.collection(COLLECTION_NAME).document(item_id)
        snapshot = document.get()
        if not snapshot.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 data 문서를 찾을 수 없습니다.",
            )

        document.delete()
        return {"id": item_id, "deleted": True}
    except HTTPException:
        raise
    except Exception as error:
        raise _firestore_unavailable(error) from error
