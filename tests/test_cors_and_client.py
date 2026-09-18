"""CORS 설정과 Firebase 클라이언트 초기화를 검증한다."""

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend import firebase_client
from backend.config import ALLOWED_ORIGINS, _parse_origins
from backend.main import app


class AllowedOriginParsingTests(unittest.TestCase):
    def test_comma_separated_values_are_split(self):
        self.assertEqual(
            _parse_origins("https://a.vercel.app,http://localhost:5500"),
            ["https://a.vercel.app", "http://localhost:5500"],
        )

    def test_blank_items_and_spaces_are_ignored(self):
        self.assertEqual(_parse_origins(" https://a.app , , https://b.app "), ["https://a.app", "https://b.app"])

    def test_empty_value_gives_an_empty_list(self):
        self.assertEqual(_parse_origins("  "), [])


class CorsBehaviourTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.allowed_origin = ALLOWED_ORIGINS[0]

    def test_configured_origin_gets_the_allow_header(self):
        response = self.client.options(
            "/api/data",
            headers={
                "Origin": self.allowed_origin,
                "Access-Control-Request-Method": "GET",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers["access-control-allow-origin"], self.allowed_origin
        )

    def test_unconfigured_origin_is_refused(self):
        response = self.client.options(
            "/api/data",
            headers={
                "Origin": "https://attacker.example.com",
                "Access-Control-Request-Method": "GET",
            },
        )

        self.assertNotEqual(response.status_code, 200)
        self.assertNotIn("access-control-allow-origin", response.headers)

    def test_credentials_are_not_allowed(self):
        # 쿠키 기반 인증을 쓰지 않으므로 허용해서는 안 된다.
        response = self.client.options(
            "/api/data",
            headers={
                "Origin": self.allowed_origin,
                "Access-Control-Request-Method": "GET",
            },
        )

        self.assertNotIn("access-control-allow-credentials", response.headers)


class ServiceAccountLoadingTests(unittest.TestCase):
    def test_invalid_json_is_rejected_without_echoing_the_value(self):
        broken = '{"private_key": "SECRET-VALUE", '

        with self.assertRaises(RuntimeError) as caught:
            firebase_client._load_service_account(broken)

        self.assertNotIn("SECRET-VALUE", str(caught.exception))

    def test_json_array_is_not_accepted_as_a_service_account(self):
        # 현재 구현은 "{"로 시작하는 값만 JSON으로 보고, 나머지는 파일 경로로 취급한다.
        # 배열은 파일 경로로 넘어가 존재하지 않는 파일 오류가 된다. 조용히 통과하지 않는 것이 핵심이다.
        with self.assertRaises(FileNotFoundError):
            firebase_client._load_service_account('["not", "an", "object"]')

    def test_empty_value_names_the_environment_variable(self):
        with self.assertRaises(RuntimeError) as caught:
            firebase_client._load_service_account("   ")

        self.assertIn("FIREBASE_SERVICE_ACCOUNT_JSON", str(caught.exception))

    def test_missing_file_reports_the_paths_that_were_checked(self):
        with self.assertRaises(FileNotFoundError) as caught:
            firebase_client._load_service_account("없는-서비스계정.json")

        self.assertIn("없는-서비스계정.json", str(caught.exception))


class FirebaseInitialisationTests(unittest.TestCase):
    def test_existing_app_is_reused_without_new_credentials(self):
        sentinel = object()
        with patch.object(firebase_client, "_get_existing_app", return_value=sentinel):
            with patch.object(firebase_client.firebase_admin, "initialize_app") as init:
                result = firebase_client.initialize_firebase()

        self.assertIs(result, sentinel)
        init.assert_not_called()

    def test_firestore_client_is_built_from_the_initialised_app(self):
        app_sentinel = object()
        client_sentinel = object()
        with patch.object(
            firebase_client, "initialize_firebase", return_value=app_sentinel
        ):
            with patch.object(
                firebase_client.firestore, "client", return_value=client_sentinel
            ) as firestore_client:
                result = firebase_client.get_firestore_client()

        self.assertIs(result, client_sentinel)
        firestore_client.assert_called_once_with(app=app_sentinel)


if __name__ == "__main__":
    unittest.main()
