"""외부 Firebase 접속 없이 설정 검증 로직을 테스트한다."""

import json
import os
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier, Lock
from tempfile import TemporaryDirectory
from unittest.mock import patch

from backend.firebase_client import (
    FIREBASE_SERVICE_ACCOUNT_ENV,
    FIREBASE_SERVICE_ACCOUNT_FILE_ENV,
    FirebaseConfigurationError,
    _load_service_account,
    _parse_service_account_json,
    get_firestore_client,
    initialize_firebase_app,
)


VALID_SERVICE_ACCOUNT = {
    "type": "service_account",
    "project_id": "test-project",
    "private_key": "test-private-key",
    "client_email": "test@test-project.iam.gserviceaccount.com",
    "token_uri": "https://oauth2.googleapis.com/token",
}


class ParseServiceAccountJsonTests(unittest.TestCase):
    def test_accepts_required_service_account_fields(self):
        result = _parse_service_account_json(json.dumps(VALID_SERVICE_ACCOUNT))

        self.assertEqual(result["project_id"], "test-project")

    def test_rejects_invalid_json(self):
        with self.assertRaisesRegex(FirebaseConfigurationError, "JSON 형식"):
            _parse_service_account_json("not-json")

    def test_rejects_missing_required_fields(self):
        incomplete_account = {"type": "service_account"}

        with self.assertRaisesRegex(FirebaseConfigurationError, "필수 항목"):
            _parse_service_account_json(json.dumps(incomplete_account))

    def test_rejects_wrong_credential_type(self):
        wrong_type_account = {**VALID_SERVICE_ACCOUNT, "type": "authorized_user"}

        with self.assertRaisesRegex(FirebaseConfigurationError, "service_account"):
            _parse_service_account_json(json.dumps(wrong_type_account))


class LoadServiceAccountTests(unittest.TestCase):
    def test_loads_service_account_from_file(self):
        with TemporaryDirectory() as temporary_directory:
            service_account_path = Path(temporary_directory) / "service-account.json"
            service_account_path.write_text(
                json.dumps(VALID_SERVICE_ACCOUNT),
                encoding="utf-8",
            )

            with patch.dict(
                os.environ,
                {
                    FIREBASE_SERVICE_ACCOUNT_ENV: "",
                    FIREBASE_SERVICE_ACCOUNT_FILE_ENV: str(service_account_path),
                },
            ):
                result = _load_service_account()

        self.assertEqual(result, VALID_SERVICE_ACCOUNT)

    def test_environment_json_takes_priority_over_file(self):
        with patch.dict(
            os.environ,
            {
                FIREBASE_SERVICE_ACCOUNT_ENV: json.dumps(VALID_SERVICE_ACCOUNT),
                FIREBASE_SERVICE_ACCOUNT_FILE_ENV: "missing-file.json",
            },
        ):
            result = _load_service_account()

        self.assertEqual(result, VALID_SERVICE_ACCOUNT)


class InitializeFirebaseAppTests(unittest.TestCase):
    def test_reuses_existing_default_app(self):
        existing_app = object()

        with patch("backend.firebase_client.firebase_admin.get_app") as get_app:
            get_app.return_value = existing_app

            result = initialize_firebase_app()

        self.assertIs(result, existing_app)

    def test_initializes_default_app_from_environment_json(self):
        service_account_json = json.dumps(VALID_SERVICE_ACCOUNT)
        credential = object()
        initialized_app = object()

        with (
            patch.dict(
                os.environ,
                {FIREBASE_SERVICE_ACCOUNT_ENV: service_account_json},
            ),
            patch(
                "backend.firebase_client.firebase_admin.get_app",
                side_effect=ValueError,
            ),
            patch(
                "backend.firebase_client.credentials.Certificate",
                return_value=credential,
            ) as certificate,
            patch(
                "backend.firebase_client.firebase_admin.initialize_app",
                return_value=initialized_app,
            ) as initialize_app,
        ):
            result = initialize_firebase_app()

        self.assertIs(result, initialized_app)
        certificate.assert_called_once_with(VALID_SERVICE_ACCOUNT)
        initialize_app.assert_called_once_with(credential)

    def test_concurrent_initialization_returns_same_app(self):
        worker_count = 4
        first_lookup_barrier = Barrier(worker_count)
        state_lock = Lock()
        state = {"app": None}
        credential = object()
        initialized_app = object()
        service_account_json = json.dumps(VALID_SERVICE_ACCOUNT)

        def get_app_after_initial_lookup():
            with state_lock:
                existing_app = state["app"]

            if existing_app is not None:
                return existing_app

            first_lookup_barrier.wait(timeout=5)
            raise ValueError("The default Firebase app does not exist.")

        def initialize_default_app(_credential):
            with state_lock:
                if state["app"] is None:
                    state["app"] = initialized_app
                    return initialized_app

            raise ValueError("The default Firebase app already exists.")

        def initialize_from_worker(_worker_number):
            return initialize_firebase_app()

        with (
            patch.dict(
                os.environ,
                {FIREBASE_SERVICE_ACCOUNT_ENV: service_account_json},
            ),
            patch(
                "backend.firebase_client.firebase_admin.get_app",
                side_effect=get_app_after_initial_lookup,
            ),
            patch(
                "backend.firebase_client.credentials.Certificate",
                return_value=credential,
            ),
            patch(
                "backend.firebase_client.firebase_admin.initialize_app",
                side_effect=initialize_default_app,
            ),
        ):
            with ThreadPoolExecutor(max_workers=worker_count) as executor:
                results = list(
                    executor.map(initialize_from_worker, range(worker_count))
                )

        self.assertTrue(all(result is initialized_app for result in results))

    def test_reports_missing_environment_variable_without_exposing_a_secret(self):
        with (
            patch.dict(
                os.environ,
                {
                    FIREBASE_SERVICE_ACCOUNT_ENV: "",
                    FIREBASE_SERVICE_ACCOUNT_FILE_ENV: "",
                },
            ),
            patch(
                "backend.firebase_client.firebase_admin.get_app",
                side_effect=ValueError,
            ),
        ):
            with self.assertRaisesRegex(
                FirebaseConfigurationError, FIREBASE_SERVICE_ACCOUNT_ENV
            ):
                initialize_firebase_app()

    def test_rejects_invalid_certificate_without_external_connection(self):
        service_account_json = json.dumps(VALID_SERVICE_ACCOUNT)

        with (
            patch.dict(
                os.environ,
                {FIREBASE_SERVICE_ACCOUNT_ENV: service_account_json},
            ),
            patch(
                "backend.firebase_client.firebase_admin.get_app",
                side_effect=ValueError,
            ),
        ):
            with self.assertRaisesRegex(
                FirebaseConfigurationError, "인증서 정보"
            ):
                initialize_firebase_app()


class GetFirestoreClientTests(unittest.TestCase):
    def test_returns_client_for_initialized_app(self):
        initialized_app = object()
        firestore_client = object()

        with (
            patch(
                "backend.firebase_client.initialize_firebase_app",
                return_value=initialized_app,
            ),
            patch(
                "backend.firebase_client.firestore.client",
                return_value=firestore_client,
            ) as create_client,
        ):
            result = get_firestore_client()

        self.assertIs(result, firestore_client)
        create_client.assert_called_once_with(app=initialized_app)


if __name__ == "__main__":
    unittest.main()
