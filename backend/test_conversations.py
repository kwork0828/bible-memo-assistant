"""외부 Firestore 없이 대화·암송 회고 API를 검증한다."""

import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.main import app


class FakeDocument:
    def __init__(self, document_id):
        self.id = document_id
        self.payload = None

    def set(self, payload):
        self.payload = payload

    def get(self):
        return SimpleNamespace(
            id=self.id,
            exists=self.payload is not None,
            to_dict=lambda: self.payload or {},
        )

    def delete(self):
        self.payload = None

    def to_dict(self):
        return self.payload or {}


class FakeCollection:
    def __init__(self):
        self.documents = {}

    def document(self, document_id=None):
        document_id = document_id or f"conversation-{len(self.documents) + 1}"
        return self.documents.setdefault(document_id, FakeDocument(document_id))

    def stream(self):
        return [document for document in self.documents.values() if document.payload is not None]


class FakeClient:
    def __init__(self):
        self.collections = {"conversations": FakeCollection()}

    def collection(self, name):
        return self.collections[name]


class ConversationApiTests(unittest.TestCase):
    def setUp(self):
        self.fake_client = FakeClient()
        self.client = TestClient(app)
        self.patcher = patch(
            "backend.routers.conversations.get_firestore_client",
            return_value=self.fake_client,
        )
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def test_create_list_and_get_conversation_with_reflections(self):
        response = self.client.post(
            "/api/conversations",
            json={
                "title": "Philippians 4:13 묵상",
                "messages": [{"role": "user", "content": "오늘 적용을 도와줘"}],
                "god_reflection": "하나님은 힘을 주시는 분이라고 느꼈다.",
                "today_application": "불안한 동료에게 먼저 연락한다.",
                "yesterday_application": "아이와 약속한 시간을 지켰다.",
            },
        )
        self.assertEqual(response.status_code, 201)
        document_id = response.json()["id"]
        self.assertTrue(datetime.fromisoformat(response.json()["created_at"]))

        listed = self.client.get("/api/conversations")
        self.assertEqual(len(listed.json()), 1)
        self.assertEqual(listed.json()[0]["god_reflection"], "하나님은 힘을 주시는 분이라고 느꼈다.")

        loaded = self.client.get(f"/api/conversations/{document_id}")
        self.assertEqual(loaded.status_code, 200)
        self.assertEqual(loaded.json()["messages"][0]["role"], "user")

    def test_delete_conversation(self):
        response = self.client.post("/api/conversations", json={})
        document_id = response.json()["id"]
        deleted = self.client.delete(f"/api/conversations/{document_id}")
        self.assertEqual(deleted.json(), {"id": document_id, "deleted": True})

    def test_missing_conversation_returns_404(self):
        response = self.client.get("/api/conversations/not-found")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
