import os
from pathlib import Path

from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
ENV_PATH = BACKEND_DIR / ".env"

load_dotenv(ENV_PATH, override=False)


def _read_env(name: str, default: str = "") -> str:
    """환경변수를 앞뒤 공백 없이 읽는다."""
    return os.getenv(name, default).strip()


def _read_int_env(name: str, default: int) -> int:
    """정수 환경변수를 읽고 잘못된 값이면 기본값을 사용한다."""
    raw_value = _read_env(name)
    if not raw_value:
        return default
    try:
        return int(raw_value)
    except ValueError:
        return default


def _parse_origins(raw_value: str) -> list[str]:
    """쉼표로 구분된 CORS 허용 주소를 리스트로 변환한다."""
    return [origin.strip() for origin in raw_value.split(",") if origin.strip()]


FIREBASE_SERVICE_ACCOUNT_JSON = _read_env("FIREBASE_SERVICE_ACCOUNT_JSON")
ALLOWED_ORIGINS = _parse_origins(
    _read_env("ALLOWED_ORIGINS", "http://localhost:3000")
)

AI_PROVIDER = _read_env("AI_PROVIDER")
OPENAI_API_KEY = _read_env("OPENAI_API_KEY")
OPENAI_BASE_URL = _read_env("OPENAI_BASE_URL")
OPENAI_MODEL = _read_env("OPENAI_MODEL")
AI_MAX_OUTPUT_TOKENS = _read_int_env("AI_MAX_OUTPUT_TOKENS", 500)
AI_MAX_RETRIES = max(1, _read_int_env("AI_MAX_RETRIES", 2))
