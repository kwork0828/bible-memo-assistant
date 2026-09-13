"""주간·월간 요약 규칙을 검증한다."""

import unittest
from datetime import date
from backend.routers.data import _make_insight
from backend.models import DataResponse
from backend.services.summary import period_range


class SummaryTests(unittest.TestCase):
    def test_week_starts_on_monday_and_ends_on_sunday(self):
        self.assertEqual(
            period_range("week", date(2026, 9, 17)),
            (date(2026, 9, 14), date(2026, 9, 20)),
        )

    def test_month_range(self):
        self.assertEqual(
            period_range("month", date(2026, 9, 17)),
            (date(2026, 9, 1), date(2026, 9, 30)),
        )

    def test_empty_period_gives_actionable_insight(self):
        self.assertIn("5분 루틴", _make_insight([], "week"))

    def test_consistent_week_gets_positive_insight(self):
        items = [
            DataResponse(id=str(index), date=f"2026-09-{14 + index:02d}", value=20, memo="")
            for index in range(5)
        ]
        self.assertIn("5일 이상", _make_insight(items, "week"))


if __name__ == "__main__":
    unittest.main()
