"""암송 시계열 데이터를 AI와 화면에서 쓰기 쉬운 요약으로 바꾼다."""

from typing import Any


def build_data_summary(items: list[dict[str, Any]]) -> dict[str, Any]:
    """Firestore data 문서 목록을 간단한 통계 정보로 요약한다."""
    if not items:
        return {
            "count": 0,
            "total_value": 0,
            "average_value": 0,
            "first_date": None,
            "last_date": None,
        }

    values = [int(item.get("value", 0) or 0) for item in items]
    dates = sorted(
        str(item.get("date"))
        for item in items
        if item.get("date") is not None
    )
    total_value = sum(values)

    return {
        "count": len(items),
        "total_value": total_value,
        "average_value": round(total_value / len(items), 2),
        "first_date": dates[0] if dates else None,
        "last_date": dates[-1] if dates else None,
    }
