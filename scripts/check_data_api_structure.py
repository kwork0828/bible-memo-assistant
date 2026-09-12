"""Firebase 인증 없이 data API 라우트 구조만 확인하는 개발용 스크립트."""

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.main import app
from backend.models import DataCreate
from backend.services.summary import build_data_summary


REQUIRED_ROUTES = {
    ("/api/data", "POST"),
    ("/api/data", "GET"),
    ("/api/data/{document_id}", "PUT"),
    ("/api/data/{document_id}", "DELETE"),
    ("/api/data/summary", "GET"),
}


def main() -> int:
    actual_routes = set()
    for route in app.routes:
        methods = getattr(route, "methods", None) or set()
        for method in methods:
            actual_routes.add((route.path, method))

    missing = sorted(REQUIRED_ROUTES - actual_routes)
    if missing:
        print("DATA_API_STRUCTURE_FAILED")
        for path, method in missing:
            print(f"MISSING: {method} {path}")
        return 1

    sample = DataCreate(
        date="2026-01-01",
        value=10,
        memo={"new": [], "review": []},
    )
    summary = build_data_summary([sample.model_dump()])

    if summary["count"] != 1 or summary["total_value"] != 10:
        print("DATA_API_STRUCTURE_FAILED: summary 검증 실패")
        return 1

    print("DATA_API_STRUCTURE_OK")
    print("Firebase 연결 없이 필수 라우트와 기본 데이터 모델/요약 로직을 확인했습니다.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
