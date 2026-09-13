"""기간별 학습 기록 요약을 위한 순수 함수."""

from datetime import date, timedelta
from typing import Literal


def period_range(period: Literal["week", "month"], today: date) -> tuple[date, date]:
    """기준일이 포함된 주간 또는 월간 범위를 반환한다."""
    if period == "week":
        start = today - timedelta(days=today.weekday())
        return start, start + timedelta(days=6)
    start = today.replace(day=1)
    next_month = (start.replace(day=28) + timedelta(days=4)).replace(day=1)
    return start, next_month - timedelta(days=1)
