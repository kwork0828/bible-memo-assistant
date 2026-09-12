"""로컬 Firebase 연결용 .env를 안전하게 준비하는 개발용 스크립트."""

from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
ENV_PATH = BACKEND_DIR / ".env"
SERVICE_ACCOUNT_PATH = BACKEND_DIR / "firebase-service-account.json"


def _is_git_ignored(path: Path) -> bool:
    """대상 파일이 .gitignore 규칙으로 제외되는지 확인한다."""
    result = subprocess.run(
        ["git", "check-ignore", "-q", str(path.relative_to(PROJECT_ROOT))],
        cwd=PROJECT_ROOT,
        check=False,
    )
    return result.returncode == 0


def _upsert_env_value(lines: list[str], key: str, value: str) -> list[str]:
    """기존 .env 내용은 보존하면서 지정한 키만 추가하거나 갱신한다."""
    prefix = f"{key}="
    updated = False
    result: list[str] = []

    for line in lines:
        if line.startswith(prefix):
            result.append(f"{prefix}{value}")
            updated = True
        else:
            result.append(line)

    if not updated:
        if result and result[-1] != "":
            result.append("")
        result.append(f"{prefix}{value}")

    return result


def main() -> int:
    if not SERVICE_ACCOUNT_PATH.exists():
        print(
            "SETUP_FAILED: backend/firebase-service-account.json 파일을 찾을 수 없습니다."
        )
        return 1

    if not _is_git_ignored(SERVICE_ACCOUNT_PATH):
        print(
            "SETUP_BLOCKED: Firebase 서비스 계정 파일이 Git에서 제외되지 않았습니다. "
            ".gitignore를 먼저 확인하세요."
        )
        return 1

    if not _is_git_ignored(ENV_PATH):
        print(
            "SETUP_BLOCKED: backend/.env 파일이 Git에서 제외되지 않았습니다. "
            ".gitignore를 먼저 확인하세요."
        )
        return 1

    existing_lines = []
    if ENV_PATH.exists():
        existing_lines = ENV_PATH.read_text(encoding="utf-8").splitlines()

    lines = _upsert_env_value(
        existing_lines,
        "FIREBASE_SERVICE_ACCOUNT_JSON",
        "backend/firebase-service-account.json",
    )
    lines = _upsert_env_value(
        lines,
        "ALLOWED_ORIGINS",
        "http://localhost:3000",
    )

    ENV_PATH.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    print("LOCAL_FIREBASE_ENV_OK")
    print("Firebase 키 내용은 출력하지 않았습니다.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
