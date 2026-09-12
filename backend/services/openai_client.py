"""OpenAI-compatible AI Provider 호출을 한 곳에서 관리한다."""

import json
import logging
import time
from typing import Any

from openai import OpenAI

from backend.config import (
    AI_MAX_OUTPUT_TOKENS,
    AI_MAX_RETRIES,
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    OPENAI_MODEL,
)


logger = logging.getLogger(__name__)
THOUGHT_KEYS = {"thought", "thinking", "reasoning", "analysis"}


def get_openai_client() -> OpenAI:
    """환경변수로 OpenAI 또는 OpenAI-compatible 클라이언트를 만든다."""
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")

    kwargs: dict[str, Any] = {"api_key": OPENAI_API_KEY}
    if OPENAI_BASE_URL:
        kwargs["base_url"] = OPENAI_BASE_URL
    return OpenAI(**kwargs)


def list_available_models() -> list[str]:
    """실제 Provider가 응답한 모델 ID만 반환한다."""
    client = get_openai_client()
    return sorted(model.id for model in client.models.list().data)


def _strip_code_fence(text: str) -> str:
    """모델이 실수로 붙인 ```json 코드 펜스를 제거한다."""
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines:
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    return stripped


def _remove_thought_fields(value: Any) -> Any:
    """사용자에게 노출할 JSON에서 thought/reasoning 계열 필드를 제거한다."""
    if isinstance(value, dict):
        return {
            key: _remove_thought_fields(item)
            for key, item in value.items()
            if key.lower() not in THOUGHT_KEYS
        }
    if isinstance(value, list):
        return [_remove_thought_fields(item) for item in value]
    return value


def _parse_json_reply(content: str) -> str:
    """AI JSON 응답에서 최종 사용자 답변 문자열만 꺼낸다."""
    cleaned_text = _strip_code_fence(content)
    try:
        parsed = json.loads(cleaned_text)
    except json.JSONDecodeError as error:
        raise RuntimeError("AI 응답이 올바른 JSON 형식이 아닙니다.") from error

    cleaned = _remove_thought_fields(parsed)
    if not isinstance(cleaned, dict):
        raise RuntimeError("AI JSON 응답은 객체 형태여야 합니다.")

    for key in ("reply", "answer"):
        value = cleaned.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    raise RuntimeError("AI JSON 응답에 reply 또는 answer 문자열이 없습니다.")


def generate_chat_reply(system_prompt: str, messages: list[dict[str, str]]) -> str:
    """환경변수로 선택된 실제 모델에 JSON 채팅 응답을 요청한다."""
    if not OPENAI_MODEL:
        raise RuntimeError(
            "OPENAI_MODEL이 비어 있습니다. 먼저 실제 /v1/models 목록을 조회한 뒤 존재하는 모델명을 설정하세요."
        )

    client = get_openai_client()
    request_messages = [
        {"role": "system", "content": system_prompt},
        *messages,
    ]
    last_error: Exception | None = None

    for attempt in range(1, AI_MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=request_messages,
                max_tokens=AI_MAX_OUTPUT_TOKENS,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content
            if not isinstance(content, str) or not content.strip():
                raise RuntimeError("AI가 빈 응답을 반환했습니다.")
            return _parse_json_reply(content)
        except Exception as error:
            last_error = error
            logger.warning(
                "AI request failed (attempt %s/%s): %s",
                attempt,
                AI_MAX_RETRIES,
                type(error).__name__,
            )
            if attempt < AI_MAX_RETRIES:
                time.sleep(min(attempt, 2))

    raise RuntimeError("AI 요청이 재시도 후에도 실패했습니다.") from last_error
