"""데이터 API에서 사용하는 요청·응답 모델."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class DataCreate(BaseModel):
    """하루 암송 일정 생성 요청."""

    date: str = Field(min_length=1, description="학습 날짜(예: 2026-09-13)")
    value: int = Field(ge=0, description="해당 날짜의 총 학습 단어 수")
    memo: str = Field(default="", description="신규·복습 구절 메모")


class DataUpdate(BaseModel):
    """하루 암송 일정 수정 요청."""

    date: Optional[str] = Field(default=None, min_length=1)
    value: Optional[int] = Field(default=None, ge=0)
    memo: Optional[str] = None


class DataResponse(DataCreate):
    """Firestore 문서 ID를 포함한 일정 응답."""

    id: str


class DataSummary(BaseModel):
    """암송 일정 전체 요약."""

    total_days: int
    total_words: int
    average_words: float
    first_date: Optional[str] = None
    last_date: Optional[str] = None


class PeriodInsight(BaseModel):
    """주간 또는 월간 학습 기록과 인사이트."""

    period: Literal["week", "month"]
    start_date: str
    end_date: str
    total_days: int
    total_words: int
    average_words: float
    insight: str


class ConversationMessage(BaseModel):
    """AI 대화 한 줄."""

    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)


class ConversationCreate(BaseModel):
    """대화와 암송 후 회고 저장 요청."""

    title: str = Field(default="암송 회고", min_length=1)
    messages: list[ConversationMessage] = Field(default_factory=list)
    god_reflection: str = Field(default="", description="암송 후 하나님에 대한 묵상")
    today_application: str = Field(default="", description="오늘 말씀을 적용할 방법")
    yesterday_application: str = Field(default="", description="어제 말씀을 적용한 방법")


class ConversationResponse(ConversationCreate):
    """Firestore 문서 ID와 생성 시각을 포함한 대화 응답."""

    id: str
    created_at: datetime
