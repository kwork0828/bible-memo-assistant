from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


DATE_FORMAT = "%Y-%m-%d"


def _validate_iso_date(value: str) -> str:
    """YYYY-MM-DD 형식의 날짜 문자열만 허용한다."""
    try:
        datetime.strptime(value, DATE_FORMAT)
    except ValueError as error:
        raise ValueError("date는 YYYY-MM-DD 형식이어야 합니다.") from error
    return value


class DataBase(BaseModel):
    """하루 단위 시계열 암송 데이터의 공통 필드."""

    date: str
    value: float = Field(ge=0)
    memo: dict[str, Any] = Field(default_factory=dict)

    @field_validator("date")
    @classmethod
    def validate_date(cls, value: str) -> str:
        return _validate_iso_date(value)


class DataCreate(DataBase):
    """Firestore에 새 일정을 저장할 때 사용하는 입력 모델."""


class DataUpdate(BaseModel):
    """기존 일정의 일부 필드만 수정할 때 사용하는 입력 모델."""

    date: str | None = None
    value: float | None = Field(default=None, ge=0)
    memo: dict[str, Any] | None = None

    @field_validator("date")
    @classmethod
    def validate_date(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return _validate_iso_date(value)


class DataResponse(DataBase):
    """Firestore 문서 ID를 포함한 API 응답 모델."""

    id: str


class ConversationMessage(BaseModel):
    """대화에 저장되는 한 개의 사용자/AI 메시지."""

    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)


class ConversationCreate(BaseModel):
    """새 대화를 만들 때 사용하는 입력 모델."""

    title: str = Field(default="새 대화", min_length=1, max_length=100)
    messages: list[ConversationMessage] = Field(default_factory=list)


class ConversationResponse(ConversationCreate):
    """Firestore 문서 ID와 시간 정보를 포함한 대화 응답 모델."""

    id: str
    created_at: str
    updated_at: str
