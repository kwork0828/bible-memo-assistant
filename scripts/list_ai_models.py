"""실제 OpenAI-compatible Provider가 제공하는 모델 목록을 조회한다."""

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.services.openai_client import list_available_models


def main() -> int:
    try:
        models = list_available_models()
    except Exception as error:
        print(f"MODEL_LIST_FAILED: {error}")
        return 1

    print("MODEL_LIST_OK")
    for model in models:
        print(model)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
