"""Create a Bible memorization and review schedule from verses.txt."""

import argparse
import json
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path


REVIEW_INTERVALS = (0, 1, 3, 7, 14, 30)
MINIMUM_SUBMISSION_VERSES = 100
DEVELOPMENT_DATA_WARNING = (
    "현재 구절 수는 과제 제출 기준인 100개 미만이며 개발 테스트용 데이터입니다."
)
DEFAULT_VERSES_PATH = Path(__file__).with_name("verses.txt")


def parse_date(value: str) -> date:
    """Convert an ISO date argument to a date."""
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as error:
        raise argparse.ArgumentTypeError("날짜는 YYYY-MM-DD 형식이어야 합니다.") from error


def read_verses(path: Path) -> list[dict[str, str]]:
    """Read tab-separated verse references and text from a UTF-8 file."""
    verses = []

    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line:
            continue

        try:
            reference, text = line.split("\t", maxsplit=1)
        except ValueError as error:
            raise ValueError(
                f"{path}의 {line_number}번째 줄에 탭으로 구분된 구절 이름과 본문이 필요합니다."
            ) from error

        reference = reference.strip()
        text = text.strip()
        if not reference or not text:
            raise ValueError(f"{path}의 {line_number}번째 줄에 빈 항목이 있습니다.")

        verses.append({"reference": reference, "text": text})

    if not verses:
        raise ValueError(f"{path}에 구절이 없습니다.")

    return verses


def count_words(text: str) -> int:
    """Count whitespace-separated words in a verse."""
    return len(text.split())


def make_schedule(verses: list[dict[str, str]], start_date: date) -> list[dict]:
    """Build daily Firestore-ready schedule records."""
    daily_items = defaultdict(lambda: {"new": [], "review": []})

    for verse_index, verse in enumerate(verses):
        learning_date = start_date + timedelta(days=verse_index)
        verse_data = {
            "reference": verse["reference"],
            "text": verse["text"],
            "word_count": count_words(verse["text"]),
        }

        for review_number, interval_days in enumerate(REVIEW_INTERVALS):
            scheduled_date = learning_date + timedelta(days=interval_days)
            if interval_days == 0:
                daily_items[scheduled_date]["new"].append(verse_data.copy())
            else:
                review_data = verse_data.copy()
                review_data["review_number"] = review_number
                review_data["interval_days"] = interval_days
                daily_items[scheduled_date]["review"].append(review_data)

    schedule = []
    for scheduled_date in sorted(daily_items):
        memo = daily_items[scheduled_date]
        all_items = memo["new"] + memo["review"]
        schedule.append(
            {
                "date": scheduled_date.isoformat(),
                "value": sum(item["word_count"] for item in all_items),
                "memo": memo,
            }
        )

    return schedule


def build_parser() -> argparse.ArgumentParser:
    """Create command-line arguments for reproducible development runs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--verses",
        type=Path,
        default=DEFAULT_VERSES_PATH,
        help="구절 입력 파일 경로 (기본값: scripts/verses.txt)",
    )
    parser.add_argument(
        "--start-date",
        type=parse_date,
        default=date.today(),
        help="첫 신규 학습일, YYYY-MM-DD (기본값: 오늘)",
    )
    return parser


def main() -> int:
    """Read verses, warn about development data, and print schedule JSON."""
    args = build_parser().parse_args()

    try:
        verses = read_verses(args.verses)
    except (OSError, ValueError) as error:
        print(f"오류: {error}", file=sys.stderr)
        return 1

    if len(verses) < MINIMUM_SUBMISSION_VERSES:
        print(f"경고: {DEVELOPMENT_DATA_WARNING}", file=sys.stderr)

    schedule = make_schedule(verses, args.start_date)
    print(json.dumps(schedule, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())