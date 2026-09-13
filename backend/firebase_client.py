"""Firebase Admin SDK와 Firestore 클라이언트를 안전하게 초기화한다."""

import json
import os
from pathlib import Path
from typing import Any

import firebase_admin
from dotenv import load_dotenv
from firebase_admin import credentials, firestore


FIREBASE_SERVICE_ACCOUNT_ENV = "FIREBASE_SERVICE_ACCOUNT_JSON"
FIREBASE_SERVICE_ACCOUNT_FILE_ENV = "FIREBASE_SERVICE_ACCOUNT_FILE"
REQUIRED_SERVICE_ACCOUNT_FIELDS = {
    "type",
    "project_id",
    "private_key",
    "client_email",
    "token_uri",
}

# 로컬에서는 backend/.env를 읽고, Render에서는 이미 설정된 환경변수를 유지한다.
load_dotenv(dotenv_path=Path(__file__).with_name(".env"), override=False)


class FirebaseConfigurationError(RuntimeError):
    """Firebase 설정이 없거나 올바르지 않을 때 발생한다."""


def _parse_service_account_json(raw_value: str) -> dict[str, Any]:
    """환경변수의 서비스 계정 JSON을 읽고 필수 항목을 검사한다."""
    try:
        service_account = json.loads(raw_value)
    except json.JSONDecodeError as error:
        raise FirebaseConfigurationError(
            f"{FIREBASE_SERVICE_ACCOUNT_ENV} 값이 올바른 JSON 형식이 아닙니다."
        ) from error

    if not isinstance(service_account, dict):
        raise FirebaseConfigurationError(
            f"{FIREBASE_SERVICE_ACCOUNT_ENV} 값은 JSON 객체여야 합니다."
        )

    missing_fields = sorted(
        field for field in REQUIRED_SERVICE_ACCOUNT_FIELDS if not service_account.get(field)
    )
    if missing_fields:
        raise FirebaseConfigurationError(
            "Firebase 서비스 계정 JSON에 필수 항목이 없습니다: "
            + ", ".join(missing_fields)
        )

    if service_account["type"] != "service_account":
        raise FirebaseConfigurationError(
            "Firebase 인증 정보의 type은 service_account여야 합니다."
        )

    return service_account


def _load_service_account() -> dict[str, Any]:
    """환경변수의 JSON 또는 로컬 키 파일에서 서비스 계정 정보를 읽는다."""
    raw_service_account = os.getenv(FIREBASE_SERVICE_ACCOUNT_ENV, "").strip()
    if raw_service_account:
        return _parse_service_account_json(raw_service_account)

    file_value = os.getenv(FIREBASE_SERVICE_ACCOUNT_FILE_ENV, "").strip()
    if not file_value:
        raise FirebaseConfigurationError(
            f"{FIREBASE_SERVICE_ACCOUNT_ENV} 또는 "
            f"{FIREBASE_SERVICE_ACCOUNT_FILE_ENV} 환경변수가 설정되지 않았습니다."
        )

    service_account_path = Path(file_value)
    if not service_account_path.is_absolute():
        service_account_path = Path(__file__).parent / service_account_path

    try:
        raw_service_account = service_account_path.read_text(encoding="utf-8")
    except OSError as error:
        raise FirebaseConfigurationError(
            f"{FIREBASE_SERVICE_ACCOUNT_FILE_ENV}에 지정한 파일을 읽을 수 없습니다."
        ) from error

    return _parse_service_account_json(raw_service_account)


def initialize_firebase_app() -> firebase_admin.App:
    """기본 Firebase 앱을 한 번만 초기화해 반환한다."""
    try:
        return firebase_admin.get_app()
    except ValueError:
        pass

    service_account = _load_service_account()

    try:
        credential = credentials.Certificate(service_account)
    except (KeyError, ValueError) as error:
        raise FirebaseConfigurationError(
            "Firebase 서비스 계정 JSON의 인증서 정보가 올바르지 않습니다."
        ) from error

    try:
        return firebase_admin.initialize_app(credential)
    except ValueError as error:
        if "already exists" in str(error).lower():
            try:
                return firebase_admin.get_app()
            except ValueError:
                pass

        raise FirebaseConfigurationError(
            "Firebase 앱을 초기화하지 못했습니다."
        ) from error


def get_firestore_client():
    """초기화된 Firebase 앱에 연결된 Firestore 클라이언트를 반환한다."""
    app = initialize_firebase_app()
    return firestore.client(app=app)
