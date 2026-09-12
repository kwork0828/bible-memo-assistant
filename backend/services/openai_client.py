from openai import OpenAI

from backend.config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL


DEFAULT_MAX_COMPLETION_TOKENS = 500


def get_openai_client() -> OpenAI:
    """OpenAI 또는 OpenAI-compatible API 클라이언트를 생성한다."""
    if not OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY 환경변수가 비어 있습니다. 실제 키는 backend/.env 또는 배포 환경변수에 설정하세요."
        )

    client_kwargs = {"api_key": OPENAI_API_KEY}
    if OPENAI_BASE_URL:
        client_kwargs["base_url"] = OPENAI_BASE_URL

    return OpenAI(**client_kwargs)


def list_available_models() -> list[str]:
    """실제 API가 반환한 사용 가능 모델 ID를 정렬해 반환한다."""
    client = get_openai_client()
    result = client.models.list()
    return sorted(model.id for model in result.data)


def create_chat_reply(
    messages: list[dict[str, str]],
    max_completion_tokens: int = DEFAULT_MAX_COMPLETION_TOKENS,
) -> str:
    """환경변수에 실제 확인된 모델이 설정된 경우에만 채팅 응답을 생성한다."""
    if not OPENAI_MODEL:
        raise RuntimeError(
            "OPENAI_MODEL 환경변수가 비어 있습니다. 먼저 실제 /v1/models 목록을 조회해 존재하는 모델을 선택하세요."
        )

    client = get_openai_client()
    completion = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        max_completion_tokens=max_completion_tokens,
    )

    content = completion.choices[0].message.content
    if not content:
        raise RuntimeError("AI API가 비어 있는 응답을 반환했습니다.")

    return content.strip()
