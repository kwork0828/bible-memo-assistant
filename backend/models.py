"""API 요청 데이터의 형식과 기본 검증 규칙을 정의한다."""

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class DataCreate(BaseModel):
    """하루 암송 일정 데이터를 새로 저장할 때 사용하는 입력 형식."""

    date: str
    value: int = Field(ge=0)
    memo: dict[str, Any] = Field(default_factory=dict)

    @field_validator("date")
    @classmethod
    def validate_date(cls, value: str) -> str:
        """날짜가 YYYY-MM-DD 형식인지 확인한다."""
        try:
            date.fromisoformat(value)
        except ValueError as error:
            raise ValueError("date는 YYYY-MM-DD 형식이어야 합니다.") from error
        return value


class DataUpdate(BaseModel):
    """기존 암송 일정에서 바꿀 값만 전달할 때 사용하는 입력 형식."""

    date: str | None = None
    value: int | None = Field(default=None, ge=0)
    memo: dict[str, Any] | None = None

    @field_validator("date")
    @classmethod
    def validate_date(cls, value: str | None) -> str | None:
        if value is None:
            return value
        try:
            date.fromisoformat(value)
        except ValueError as error:
            raise ValueError("date는 YYYY-MM-DD 형식이어야 합니다.") from error
        return value


class ChatMessage(BaseModel):
    """대화 한 줄의 역할과 내용을 표현한다."""

    role: Literal["user", "assistant", "system"]
    content: str = Field(min_length=1)


class ConversationCreate(BaseModel):
    """새 대화를 저장할 때 사용하는 입력 형식."""

    title: str = Field(default="새 대화", min_length=1, max_length=120)
    messages: list[ChatMessage] = Field(default_factory=list)
