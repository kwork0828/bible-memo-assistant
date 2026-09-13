"""FastAPI 앱의 CORS 환경변수 설정을 테스트한다."""

import importlib
import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend import main


class AllowedOriginsTests(unittest.TestCase):
    def test_uses_local_defaults_when_environment_value_is_empty(self):
        with patch.dict(os.environ, {"ALLOWED_ORIGINS": ""}):
            result = main.get_allowed_origins()

        self.assertEqual(result, main.DEFAULT_ALLOWED_ORIGINS)

    def test_parses_comma_separated_origins_and_ignores_empty_items(self):
        with patch.dict(
            os.environ,
            {
                "ALLOWED_ORIGINS": (
                    " https://frontend.example.com, "
                    "http://localhost:5500, ,"
                )
            },
        ):
            result = main.get_allowed_origins()

        self.assertEqual(
            result,
            [
                "https://frontend.example.com",
                "http://localhost:5500",
            ],
        )


class CorsHeaderTests(unittest.TestCase):
    def _create_client(self, allowed_origins: str) -> TestClient:
        with patch.dict(os.environ, {"ALLOWED_ORIGINS": allowed_origins}):
            reloaded_main = importlib.reload(main)

        self.addCleanup(importlib.reload, main)
        return TestClient(reloaded_main.app)

    def test_allows_configured_origin(self):
        client = self._create_client("https://frontend.example.com")

        response = client.options(
            "/",
            headers={
                "Origin": "https://frontend.example.com",
                "Access-Control-Request-Method": "GET",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("access-control-allow-origin"),
            "https://frontend.example.com",
        )

    def test_rejects_unconfigured_origin(self):
        client = self._create_client("https://frontend.example.com")

        response = client.options(
            "/",
            headers={
                "Origin": "https://untrusted.example.com",
                "Access-Control-Request-Method": "GET",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIsNone(response.headers.get("access-control-allow-origin"))


if __name__ == "__main__":
    unittest.main()
