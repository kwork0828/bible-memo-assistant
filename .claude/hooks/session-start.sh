#!/bin/bash
# Claude Code on the web(원격 세션)에서 이 저장소를 바로 실행·테스트할 수 있게 준비한다.
# 로컬 Windows/PowerShell 개발 환경에는 영향을 주지 않는다.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
cd "$PROJECT_DIR"

VENV_DIR="$PROJECT_DIR/.venv"
REQUIREMENTS="$PROJECT_DIR/backend/requirements.txt"

# 가상환경을 쓰는 이유: 컨테이너의 시스템 파이썬에는 배포판이 설치한 패키지가 섞여 있어
# requirements.txt의 고정 버전과 충돌한다(예: PyJWT 제거 실패).
# 이미 만들어져 있으면 다시 만들지 않는다.
if [ ! -x "$VENV_DIR/bin/python" ]; then
  python3 -m venv "$VENV_DIR"
fi

if [ -f "$REQUIREMENTS" ]; then
  "$VENV_DIR/bin/python" -m pip install --quiet --disable-pip-version-check -r "$REQUIREMENTS"
fi

# 이후 모든 명령이 .venv 파이썬을 쓰고, 어느 경로에서든 backend 패키지를 import 할 수 있게 한다.
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  {
    echo "export PATH=\"$VENV_DIR/bin:\$PATH\""
    echo "export PYTHONPATH=\"$PROJECT_DIR\""
  } >> "$CLAUDE_ENV_FILE"
fi

echo "환경 준비 완료: $("$VENV_DIR/bin/python" --version), backend/requirements.txt 설치됨"
