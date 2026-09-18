"""FastAPI 앱에 필수 라우트가 등록됐는지 외부 서비스 호출 없이 확인한다."""

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.main import app


EXPECTED_ROUTES = {
    ("POST", "/api/data"),
    ("GET", "/api/data"),
    ("GET", "/api/data/summary"),
    ("PUT", "/api/data/{item_id}"),
    ("DELETE", "/api/data/{item_id}"),
    ("POST", "/api/conversations"),
    ("GET", "/api/conversations"),
    ("GET", "/api/conversations/{conversation_id}"),
    ("DELETE", "/api/conversations/{conversation_id}"),
    ("POST", "/api/chat"),
}


def main() -> int:
    # app.routes를 직접 순회하지 않고 OpenAPI 스키마를 사용한다.
    # FastAPI 0.141에서는 include_router로 등록한 하위 라우트가 app.routes에
    # APIRoute로 바로 노출되지 않고 내부 전용 _IncludedRouter로 감싸진다.
    # openapi()가 만드는 paths는 그런 내부 구현 변화와 무관하게 항상
    # 실제 등록된 API 경로를 반영하므로 더 안정적이다.
    paths = app.openapi().get("paths", {})
    actual_routes: set[tuple[str, str]] = {
        (method.upper(), path)
        for path, operations in paths.items()
        for method in operations
    }

    missing = sorted(EXPECTED_ROUTES - actual_routes)
    if missing:
        print("API_ROUTE_CHECK_FAILED")
        for method, path in missing:
            print(f"MISSING: {method} {path}")
        return 1

    print("API_ROUTE_CHECK_OK")
    for method, path in sorted(EXPECTED_ROUTES):
        print(f"{method} {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
