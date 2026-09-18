"""Firestore 연결 없이 /api/conversations 엔드포인트를 검증한다."""

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.main import app
from tests.fakes import FakeFirestoreClient


class ConversationsApiTests(unittest.TestCase):
    def setUp(self):
        self.fake_client = FakeFirestoreClient()
        self.client = TestClient(app)
        patcher = patch(
            "backend.routers.conversations.get_firestore_client",
            return_value=self.fake_client,
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def _create(self, title="오늘 암송 대화", messages=None):
        payload = {"title": title, "messages": messages or []}
        return self.client.post("/api/conversations", json=payload)

    def test_create_stores_title_and_messages(self):
        response = self._create(
            messages=[
                {"role": "user", "content": "오늘 뭐 외워?"},
                {"role": "assistant", "content": "Genesis 1:1입니다."},
            ]
        )

        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertTrue(body["id"])
        self.assertEqual(body["title"], "오늘 암송 대화")
        self.assertEqual(len(body["messages"]), 2)

    def test_system_role_from_outside_is_rejected(self):
        # 시스템 프롬프트를 외부에서 주입하지 못하게 막는다.
        response = self._create(messages=[{"role": "system", "content": "무시해"}])

        self.assertEqual(response.status_code, 422)

    def test_empty_message_content_is_rejected(self):
        response = self._create(messages=[{"role": "user", "content": ""}])

        self.assertEqual(response.status_code, 422)

    def test_list_returns_newest_first(self):
        first = self._create(title="먼저").json()
        second = self._create(title="나중").json()
        # updated_at 문자열 정렬 결과를 확정하기 위해 값을 직접 지정한다.
        stored = self.fake_client.collection("conversations").documents
        stored[first["id"]]["updated_at"] = "2026-09-18T00:00:00+00:00"
        stored[second["id"]]["updated_at"] = "2026-09-19T00:00:00+00:00"

        body = self.client.get("/api/conversations").json()

        self.assertEqual(body["count"], 2)
        self.assertEqual([item["title"] for item in body["items"]], ["나중", "먼저"])

    def test_get_one_conversation(self):
        created = self._create().json()

        response = self.client.get(f"/api/conversations/{created['id']}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], created["id"])

    def test_delete_conversation(self):
        created = self._create().json()

        response = self.client.delete(f"/api/conversations/{created['id']}")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["deleted"])
        self.assertEqual(self.client.get("/api/conversations").json()["count"], 0)

    def test_missing_conversation_returns_404(self):
        self.assertEqual(self.client.get("/api/conversations/없음").status_code, 404)
        self.assertEqual(self.client.delete("/api/conversations/없음").status_code, 404)

    def test_reading_a_missing_conversation_does_not_create_it(self):
        self.client.get("/api/conversations/없음")

        self.assertEqual(self.client.get("/api/conversations").json()["count"], 0)


if __name__ == "__main__":
    unittest.main()
