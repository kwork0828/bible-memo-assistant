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
}


def main() -> int:
    actual_routes: set[tuple[str, str]] = set()

    for route in app.routes:
        methods = getattr(route, "methods", None) or set()
        path = getattr(route, "path", "")
        for method in methods:
            actual_routes.add((method, path))

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
