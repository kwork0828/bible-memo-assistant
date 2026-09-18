"""Firestore 연결 없이 /api/data 엔드포인트를 검증한다."""

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.main import app
from tests.fakes import FakeFirestoreClient


SAMPLE = {
    "date": "2026-09-18",
    "value": 10,
    "memo": {"new": [{"reference": "Genesis 1:1", "word_count": 10}], "review": []},
}


class DataApiTests(unittest.TestCase):
    def setUp(self):
        self.fake_client = FakeFirestoreClient()
        self.client = TestClient(app)
        patcher = patch(
            "backend.routers.data.get_firestore_client",
            return_value=self.fake_client,
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_create_returns_201_with_generated_id_and_timestamps(self):
        response = self.client.post("/api/data", json=SAMPLE)

        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertTrue(body["id"])
        self.assertEqual(body["date"], SAMPLE["date"])
        self.assertEqual(body["value"], SAMPLE["value"])
        self.assertIn("created_at", body)
        self.assertIn("updated_at", body)

    def test_invalid_date_is_rejected_before_reaching_firestore(self):
        response = self.client.post("/api/data", json={**SAMPLE, "date": "2026-13-99"})

        self.assertEqual(response.status_code, 422)
        self.assertEqual(self.fake_client.collection("data").documents, {})

    def test_negative_value_is_rejected(self):
        response = self.client.post("/api/data", json={**SAMPLE, "value": -1})

        self.assertEqual(response.status_code, 422)

    def test_list_is_sorted_by_date(self):
        for day in ("2026-09-20", "2026-09-18", "2026-09-19"):
            self.client.post("/api/data", json={**SAMPLE, "date": day})

        body = self.client.get("/api/data").json()

        self.assertEqual(body["count"], 3)
        self.assertEqual(
            [item["date"] for item in body["items"]],
            ["2026-09-18", "2026-09-19", "2026-09-20"],
        )

    def test_summary_counts_only_stored_documents(self):
        self.client.post("/api/data", json={**SAMPLE, "value": 10})
        self.client.post("/api/data", json={**SAMPLE, "date": "2026-09-19", "value": 20})

        summary = self.client.get("/api/data/summary").json()

        self.assertEqual(summary["count"], 2)
        self.assertEqual(summary["total_value"], 30)

    def test_summary_path_is_not_captured_by_item_id_route(self):
        # /api/data/{item_id}는 PUT·DELETE만 받으므로 GET /api/data/summary가 가려지면 안 된다.
        self.assertEqual(self.client.get("/api/data/summary").status_code, 200)

    def test_update_changes_only_given_fields(self):
        created = self.client.post("/api/data", json=SAMPLE).json()

        updated = self.client.put(f"/api/data/{created['id']}", json={"value": 99})

        self.assertEqual(updated.status_code, 200)
        body = updated.json()
        self.assertEqual(body["value"], 99)
        self.assertEqual(body["date"], SAMPLE["date"])
        self.assertNotEqual(body["updated_at"], "")

    def test_update_without_any_field_is_rejected(self):
        created = self.client.post("/api/data", json=SAMPLE).json()

        response = self.client.put(f"/api/data/{created['id']}", json={})

        self.assertEqual(response.status_code, 400)

    def test_delete_removes_the_document(self):
        created = self.client.post("/api/data", json=SAMPLE).json()

        response = self.client.delete(f"/api/data/{created['id']}")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["deleted"])
        self.assertEqual(self.client.get("/api/data").json()["count"], 0)

    def test_missing_document_returns_404_for_update_and_delete(self):
        self.assertEqual(
            self.client.put("/api/data/없는문서", json={"value": 1}).status_code, 404
        )
        self.assertEqual(self.client.delete("/api/data/없는문서").status_code, 404)

    def test_reading_a_missing_document_does_not_create_it(self):
        self.client.delete("/api/data/없는문서")

        self.assertEqual(self.client.get("/api/data").json()["count"], 0)


class DataApiFirestoreFailureTests(unittest.TestCase):
    def test_firestore_failure_returns_503_without_leaking_internals(self):
        client = TestClient(app)
        secret = "service-account-private-key-ABC123"
        with patch(
            "backend.routers.data.get_firestore_client",
            side_effect=RuntimeError(secret),
        ):
            response = client.get("/api/data")

        self.assertEqual(response.status_code, 503)
        self.assertNotIn(secret, response.text)


if __name__ == "__main__":
    unittest.main()
