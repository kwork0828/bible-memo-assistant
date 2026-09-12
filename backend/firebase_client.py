import json
from pathlib import Path
from typing import Any

import firebase_admin
from firebase_admin import credentials, firestore

from backend.config import (
    BACKEND_DIR,
    FIREBASE_SERVICE_ACCOUNT_JSON,
    PROJECT_ROOT,
)


def _get_existing_app():
    """이미 초기화된 기본 Firebase 앱이 있으면 반환한다."""
    try:
        return firebase_admin.get_app()
    except ValueError:
        return None


def _load_service_account(value: str) -> str | dict[str, Any]:
    """
    서비스 계정 설정을 JSON 문자열 또는 파일 경로에서 읽는다.

    로컬에서는 파일 경로를, 배포 환경에서는 JSON 문자열을 사용할 수 있다.
    """
    raw_value = value.strip()

    if not raw_value:
        raise RuntimeError(
            "FIREBASE_SERVICE_ACCOUNT_JSON 환경변수가 비어 있습니다. "
            "로컬에서는 서비스 계정 JSON 파일 경로를, 배포 환경에서는 JSON 문자열을 설정하세요."
        )

    if raw_value.startswith("{"):
        try:
            parsed = json.loads(raw_value)
        except json.JSONDecodeError as error:
            raise RuntimeError(
                "FIREBASE_SERVICE_ACCOUNT_JSON에 들어 있는 JSON 문자열 형식이 올바르지 않습니다."
            ) from error

        if not isinstance(parsed, dict):
            raise RuntimeError(
                "FIREBASE_SERVICE_ACCOUNT_JSON JSON 값은 객체 형태여야 합니다."
            )

        return parsed

    path = Path(raw_value).expanduser()
    candidate_paths: list[Path]

    if path.is_absolute():
        candidate_paths = [path]
    else:
        candidate_paths = [PROJECT_ROOT / path, BACKEND_DIR / path]

    for candidate in candidate_paths:
        if candidate.exists() and candidate.is_file():
            return str(candidate.resolve())

    checked_paths = ", ".join(str(candidate) for candidate in candidate_paths)
    raise FileNotFoundError(
        "Firebase 서비스 계정 파일을 찾을 수 없습니다. "
        f"확인한 경로: {checked_paths}"
    )


def initialize_firebase():
    """Firebase Admin SDK를 필요할 때 한 번만 초기화한다."""
    existing_app = _get_existing_app()
    if existing_app is not None:
        return existing_app

    service_account = _load_service_account(FIREBASE_SERVICE_ACCOUNT_JSON)
    credential = credentials.Certificate(service_account)
    return firebase_admin.initialize_app(credential)


def get_firestore_client():
    """초기화된 Firebase 앱을 사용해 Firestore 클라이언트를 반환한다."""
    app = initialize_firebase()
    return firestore.client(app=app)
