"""Firestore 연결 없이 데이터 API의 CRUD와 요약을 검증한다."""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.main import app


class FakeDocument:
    def __init__(self, document_id, payload=None):
        self.id = document_id
        self.payload = payload

    def set(self, payload):
        self.payload = payload

    def get(self):
        return SimpleNamespace(
            exists=self.payload is not None,
            to_dict=lambda: self.payload or {},
        )

    def update(self, payload):
        self.payload.update(payload)

    def delete(self):
        self.payload = None

    def to_dict(self):
        return self.payload or {}


class FakeCollection:
    def __init__(self):
        self.documents = {}
        self.next_id = 1

    def document(self, document_id=None):
        if document_id is None:
            document_id = f"data-{self.next_id}"
            self.next_id += 1
        document = self.documents.setdefault(document_id, FakeDocument(document_id))
        return document

    def stream(self):
        return [document for document in self.documents.values() if document.payload is not None]


class FakeClient:
    def __init__(self):
        self.data = FakeCollection()

    def collection(self, name):
        self.assert_data_collection(name)
        return self.data

    @staticmethod
    def assert_data_collection(name):
        if name != "data":
            raise AssertionError(f"unexpected collection: {name}")


class DataApiTests(unittest.TestCase):
    def setUp(self):
        self.fake_client = FakeClient()
        self.client = TestClient(app)
        self.patcher = patch("backend.routers.data.get_firestore_client", return_value=self.fake_client)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def test_create_list_and_summary(self):
        created = self.client.post(
            "/api/data",
            json={"date": "2026-09-13", "value": 42, "memo": "Philippians 4:13"},
        )
        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.json()["id"], "data-1")

        listed = self.client.get("/api/data")
        self.assertEqual(listed.status_code, 200)
        self.assertEqual(len(listed.json()), 1)

        summary = self.client.get("/api/data/summary")
        self.assertEqual(summary.json()["total_words"], 42)
        self.assertEqual(summary.json()["average_words"], 42.0)

    def test_update_and_delete(self):
        created = self.client.post(
            "/api/data",
            json={"date": "2026-09-13", "value": 42, "memo": "old"},
        )
        document_id = created.json()["id"]

        updated = self.client.put(f"/api/data/{document_id}", json={"value": 55})
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.json()["value"], 55)
        self.assertEqual(updated.json()["memo"], "old")

        deleted = self.client.delete(f"/api/data/{document_id}")
        self.assertEqual(deleted.status_code, 200)
        self.assertTrue(deleted.json()["deleted"])

    def test_missing_document_returns_404(self):
        response = self.client.put("/api/data/not-found", json={"value": 10})
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
