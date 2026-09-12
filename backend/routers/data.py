from typing import Any

from fastapi import APIRouter, HTTPException, status

from backend.firebase_client import get_firestore_client
from backend.models import DataCreate, DataResponse, DataUpdate
from backend.services.summary import build_data_summary


router = APIRouter(prefix="/api/data", tags=["data"])
COLLECTION_NAME = "data"


def _get_collection():
    """Firestore data 컬렉션을 반환하고 설정 오류는 안전한 API 오류로 바꾼다."""
    try:
        db = get_firestore_client()
        return db.collection(COLLECTION_NAME)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firestore 연결에 실패했습니다. 서버 설정을 확인하세요.",
        ) from error


def _snapshot_to_response(snapshot) -> dict[str, Any]:
    """Firestore 문서를 API 응답 형태로 변환한다."""
    data = snapshot.to_dict() or {}
    return {"id": snapshot.id, **data}


@router.post("", response_model=DataResponse, status_code=status.HTTP_201_CREATED)
def create_data(payload: DataCreate):
    collection = _get_collection()
    document = collection.document()
    document_data = payload.model_dump()
    document.set(document_data)
    return {"id": document.id, **document_data}


@router.get("", response_model=list[DataResponse])
def list_data():
    collection = _get_collection()
    snapshots = collection.order_by("date").stream()
    return [_snapshot_to_response(snapshot) for snapshot in snapshots]


@router.get("/summary")
def get_data_summary():
    collection = _get_collection()
    records = [snapshot.to_dict() or {} for snapshot in collection.stream()]
    return build_data_summary(records)


@router.put("/{document_id}", response_model=DataResponse)
def update_data(document_id: str, payload: DataUpdate):
    collection = _get_collection()
    document = collection.document(document_id)
    current = document.get()

    if not current.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="수정할 데이터를 찾을 수 없습니다.",
        )

    changes = payload.model_dump(exclude_none=True)
    if not changes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="수정할 값을 하나 이상 보내주세요.",
        )

    document.update(changes)
    updated = document.get()
    return _snapshot_to_response(updated)


@router.delete("/{document_id}")
def delete_data(document_id: str):
    collection = _get_collection()
    document = collection.document(document_id)
    current = document.get()

    if not current.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="삭제할 데이터를 찾을 수 없습니다.",
        )

    document.delete()
    return {"status": "deleted", "id": document_id}
