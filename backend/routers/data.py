"""Firestore data 컬렉션을 다루는 API 라우터."""

from typing import Literal

from fastapi import APIRouter, HTTPException, Query, status

from backend.firebase_client import get_firestore_client
from backend.models import DataCreate, DataResponse, DataSummary, DataUpdate, PeriodInsight
from backend.services.summary import period_range


router = APIRouter(prefix="/api/data", tags=["data"])


def _document_to_response(document) -> DataResponse:
    """Firestore 문서를 API 응답 모델로 변환한다."""
    payload = document.to_dict() or {}
    return DataResponse(
        id=document.id,
        date=str(payload.get("date", "")),
        value=int(payload.get("value", 0)),
        memo=str(payload.get("memo", "")),
    )


def _get_document_reference(document_id: str):
    """문서 ID를 검증하고 Firestore 문서 참조를 반환한다."""
    if not document_id or "/" in document_id:
        raise HTTPException(status_code=400, detail="유효하지 않은 문서 ID입니다.")
    return get_firestore_client().collection("data").document(document_id)


@router.post("", response_model=DataResponse, status_code=status.HTTP_201_CREATED)
def create_data(item: DataCreate):
    """하루 암송 일정을 추가한다."""
    client = get_firestore_client()
    document_reference = client.collection("data").document()
    document_reference.set(item.model_dump())
    return DataResponse(id=document_reference.id, **item.model_dump())


@router.get("", response_model=list[DataResponse])
def list_data():
    """암송 일정을 날짜 내림차순으로 조회한다."""
    documents = get_firestore_client().collection("data").stream()
    items = [_document_to_response(document) for document in documents]
    return sorted(items, key=lambda item: item.date, reverse=True)


@router.put("/{document_id}", response_model=DataResponse)
def update_data(document_id: str, item: DataUpdate):
    """기존 암송 일정을 수정한다."""
    document_reference = _get_document_reference(document_id)
    snapshot = document_reference.get()
    if not snapshot.exists:
        raise HTTPException(status_code=404, detail="암송 일정을 찾을 수 없습니다.")

    updates = item.model_dump(exclude_unset=True)
    document_reference.update(updates)
    merged = snapshot.to_dict() or {}
    merged.update(updates)
    return DataResponse(id=document_id, **merged)


@router.delete("/{document_id}")
def delete_data(document_id: str):
    """암송 일정을 삭제한다."""
    document_reference = _get_document_reference(document_id)
    if not document_reference.get().exists:
        raise HTTPException(status_code=404, detail="암송 일정을 찾을 수 없습니다.")
    document_reference.delete()
    return {"id": document_id, "deleted": True}


@router.get("/summary", response_model=DataSummary)
def summarize_data():
    """전체 일정의 일수·단어 수·날짜 범위를 계산한다."""
    items = list_data()
    values = [item.value for item in items]
    dates = [item.date for item in items if item.date]
    return DataSummary(
        total_days=len(items),
        total_words=sum(values),
        average_words=round(sum(values) / len(values), 2) if values else 0.0,
        first_date=min(dates) if dates else None,
        last_date=max(dates) if dates else None,
    )


def _make_insight(items: list[DataResponse], period: Literal["week", "month"]) -> str:
    """학습 패턴 하나를 짧은 문장으로 설명한다."""
    if not items:
        return "아직 기록이 없습니다. 오늘 5분 루틴부터 시작해 보세요."
    active_days = len({item.date for item in items})
    average = sum(item.value for item in items) / len(items)
    if period == "week" and active_days >= 5:
        return "이번 주 5일 이상 말씀을 붙들었습니다. 지금의 짧은 리듬을 유지해 보세요."
    if period == "month" and active_days >= 20:
        return "이번 달 학습 리듬이 안정적입니다. 다음 달에는 취약 구절 복습을 한 번 더 추가해 보세요."
    if average >= 60:
        return "한 번에 학습하는 분량이 많은 편입니다. 5분씩 나누면 꾸준함을 유지하기 쉽습니다."
    return "기록이 조금씩 쌓이고 있습니다. 내일도 같은 시간에 5분을 예약해 보세요."


@router.get("/insights", response_model=PeriodInsight)
def period_insight(
    period: Literal["week", "month"] = Query(default="week"),
):
    """이번 주 또는 이번 달 학습 기록과 인사이트를 반환한다."""
    from datetime import date

    start, end = period_range(period, date.today())
    items = [
        item
        for item in list_data()
        if start.isoformat() <= item.date <= end.isoformat()
    ]
    values = [item.value for item in items]
    return PeriodInsight(
        period=period,
        start_date=start.isoformat(),
        end_date=end.isoformat(),
        total_days=len({item.date for item in items}),
        total_words=sum(values),
        average_words=round(sum(values) / len(values), 2) if values else 0.0,
        insight=_make_insight(items, period),
    )
