"""Firebase 인증 없이 conversation API 라우트와 모델 구조만 확인하는 개발용 스크립트."""

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.main import app
from backend.models import ConversationCreate


REQUIRED_ROUTES = {
    ("/api/conversations", "POST"),
    ("/api/conversations", "GET"),
    ("/api/conversations/{conversation_id}", "GET"),
    ("/api/conversations/{conversation_id}", "DELETE"),
}


def main() -> int:
    actual_routes = set()
    for route in app.routes:
        methods = getattr(route, "methods", None) or set()
        for method in methods:
            actual_routes.add((route.path, method))

    missing = sorted(REQUIRED_ROUTES - actual_routes)
    if missing:
        print("CONVERSATION_API_STRUCTURE_FAILED")
        for path, method in missing:
            print(f"MISSING: {method} {path}")
        return 1

    sample = ConversationCreate(
        title="테스트 대화",
        messages=[{"role": "user", "content": "오늘 암송 일정 알려줘"}],
    )
    if sample.messages[0].role != "user":
        print("CONVERSATION_API_STRUCTURE_FAILED: message 모델 검증 실패")
        return 1

    print("CONVERSATION_API_STRUCTURE_OK")
    print("Firebase 연결 없이 필수 대화 라우트와 기본 모델 구조를 확인했습니다.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
