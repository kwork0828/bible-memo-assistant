"""실제 AI/Firebase 호출 없이 chat API 구조를 확인하는 개발용 스크립트."""

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.main import app
from backend.models import ChatRequest


def main() -> int:
    routes = {
        (route.path, method)
        for route in app.routes
        for method in (getattr(route, "methods", None) or set())
    }

    if ("/api/chat", "POST") not in routes:
        print("CHAT_API_STRUCTURE_FAILED: POST /api/chat 누락")
        return 1

    sample = ChatRequest(message="오늘 암송 일정을 알려줘")
    if not sample.message:
        print("CHAT_API_STRUCTURE_FAILED: 요청 모델 검증 실패")
        return 1

    print("CHAT_API_STRUCTURE_OK")
    print("실제 API 호출 없이 POST /api/chat과 요청 모델 구조를 확인했습니다.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
