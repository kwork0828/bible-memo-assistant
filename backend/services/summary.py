from typing import Any


def build_data_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    """저장된 시계열 데이터를 AI와 화면에서 쓰기 쉬운 요약으로 변환한다."""
    if not records:
        return {
            "count": 0,
            "date_from": None,
            "date_to": None,
            "total_value": 0,
            "average_value": 0,
            "min_value": 0,
            "max_value": 0,
        }

    values = [float(record.get("value", 0)) for record in records]
    dates = sorted(
        str(record.get("date"))
        for record in records
        if record.get("date") is not None
    )

    total_value = sum(values)
    return {
        "count": len(records),
        "date_from": dates[0] if dates else None,
        "date_to": dates[-1] if dates else None,
        "total_value": total_value,
        "average_value": round(total_value / len(values), 2) if values else 0,
        "min_value": min(values) if values else 0,
        "max_value": max(values) if values else 0,
    }
