"""Firestore 연결 상태를 읽기 전용으로 확인하는 개발용 스크립트."""

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.firebase_client import get_firestore_client


def main() -> int:
    try:
        db = get_firestore_client()
        collection_names = sorted(collection.id for collection in db.collections())
    except Exception as error:
        print(f"FIREBASE_CONNECTION_FAILED: {error}")
        return 1

    print("FIREBASE_CONNECTION_OK")
    if collection_names:
        print("COLLECTIONS:", ", ".join(collection_names))
    else:
        print("COLLECTIONS: (none)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
