"""암송 일정을 Firestore data 컬렉션에 안전하게 넣는 시드 스크립트."""

import argparse
from datetime import date, datetime, timezone
from pathlib import Path
import sys

from google.cloud.firestore_v1.base_query import FieldFilter


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.firebase_client import get_firestore_client
from scripts.make_schedule import DEFAULT_VERSES_PATH, make_schedule, parse_date, read_verses


MINIMUM_DATA_POINTS = 100


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--verses",
        type=Path,
        default=DEFAULT_VERSES_PATH,
        help="구절 입력 파일 경로",
    )
    parser.add_argument(
        "--start-date",
        type=parse_date,
        default=date.today(),
        help="첫 신규 학습일 YYYY-MM-DD",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="실제 Firestore 쓰기를 승인한다. 생략하면 dry-run만 수행한다.",
    )
    parser.add_argument(
        "--allow-small",
        action="store_true",
        help="100개 미만 데이터도 개발 테스트 목적으로 허용한다.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    try:
        verses = read_verses(args.verses)
        schedule = make_schedule(verses, args.start_date)
    except (OSError, ValueError) as error:
        print(f"SEED_FAILED: {error}")
        return 1

    print(f"VERSES: {len(verses)}")
    print(f"DATA_POINTS: {len(schedule)}")
    print(f"START_DATE: {args.start_date.isoformat()}")

    if len(schedule) < MINIMUM_DATA_POINTS and not args.allow_small:
        print(
            "SEED_BLOCKED: 최종 제출 기준을 위해 최소 100개 이상의 시계열 데이터 포인트가 필요합니다. "
            "개발 테스트만 하려면 --allow-small을 명시하세요."
        )
        return 2

    if not args.write:
        print("DRY_RUN_OK: Firestore에는 아무 데이터도 쓰지 않았습니다.")
        print("실제 저장은 내용을 확인한 뒤 --write를 추가해야 실행됩니다.")
        return 0

    try:
        db = get_firestore_client()
        collection = db.collection("data")
        inserted = 0
        skipped = 0

        for item in schedule:
            existing = list(
                collection.where(
                    filter=FieldFilter("date", "==", item["date"])
                ).limit(1).stream()
            )
            if existing:
                skipped += 1
                continue

            now = datetime.now(timezone.utc).isoformat()
            collection.document().set(
                {
                    **item,
                    "created_at": now,
                    "updated_at": now,
                }
            )
            inserted += 1
    except Exception as error:
        print(f"SEED_FAILED: {type(error).__name__}")
        return 1

    print("SEED_WRITE_OK")
    print(f"INSERTED: {inserted}")
    print(f"SKIPPED_EXISTING_DATES: {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
