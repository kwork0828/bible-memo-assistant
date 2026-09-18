"""실제 AI 호출 없이 /api/chat 의 흐름을 검증한다.

검증 대상은 과제 요구사항의 기본 흐름이다.
데이터 요약 -> 시스템 프롬프트 주입 -> AI 호출 -> 대화 Firestore 저장
"""

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.main import app
from tests.fakes import FakeFirestoreClient


class ChatApiTests(unittest.TestCase):
    def setUp(self):
        self.fake_client = FakeFirestoreClient()
        self.client = TestClient(app)
        patcher = patch(
            "backend.routers.chat.get_firestore_client",
            return_value=self.fake_client,
        )
        patcher.start()
        self.addCleanup(patcher.stop)

        # 암송 데이터 두 건을 미리 넣어 요약이 실제로 만들어지게 한다.
        data = self.fake_client.collection("data")
        data.document("d1").set({"date": "2026-09-18", "value": 10})
        data.document("d2").set({"date": "2026-09-19", "value": 20})

    def test_summary_is_injected_into_the_system_prompt(self):
        with patch(
            "backend.routers.chat.generate_chat_reply", return_value="답변입니다."
        ) as fake_ai:
            response = self.client.post("/api/chat", json={"message": "오늘 진도 어때?"})

        self.assertEqual(response.status_code, 200)
        system_prompt = fake_ai.call_args.args[0]
        self.assertIn("30", system_prompt)  # total_value
        self.assertIn("2026-09-18", system_prompt)
        self.assertEqual(response.json()["summary"]["total_value"], 30)

    def test_reply_is_saved_as_a_new_conversation(self):
        with patch("backend.routers.chat.generate_chat_reply", return_value="답변입니다."):
            body = self.client.post("/api/chat", json={"message": "오늘 진도 어때?"}).json()

        stored = self.fake_client.collection("conversations").documents
        self.assertEqual(len(stored), 1)
        saved = stored[body["conversation_id"]]
        self.assertEqual(
            [message["role"] for message in saved["messages"]], ["user", "assistant"]
        )
        self.assertEqual(saved["messages"][1]["content"], "답변입니다.")

    def test_existing_conversation_is_continued_not_duplicated(self):
        with patch("backend.routers.chat.generate_chat_reply", return_value="첫 답변"):
            first = self.client.post("/api/chat", json={"message": "첫 질문"}).json()

        with patch("backend.routers.chat.generate_chat_reply", return_value="두번째 답변"):
            second = self.client.post(
                "/api/chat",
                json={"message": "두번째 질문", "conversation_id": first["conversation_id"]},
            ).json()

        self.assertEqual(second["conversation_id"], first["conversation_id"])
        stored = self.fake_client.collection("conversations").documents
        self.assertEqual(len(stored), 1)
        self.assertEqual(len(stored[first["conversation_id"]]["messages"]), 4)

    def test_previous_messages_are_sent_to_the_ai_as_history(self):
        with patch("backend.routers.chat.generate_chat_reply", return_value="첫 답변"):
            first = self.client.post("/api/chat", json={"message": "첫 질문"}).json()

        with patch(
            "backend.routers.chat.generate_chat_reply", return_value="두번째 답변"
        ) as fake_ai:
            self.client.post(
                "/api/chat",
                json={"message": "두번째 질문", "conversation_id": first["conversation_id"]},
            )

        sent_messages = fake_ai.call_args.args[1]
        self.assertEqual(
            [message["content"] for message in sent_messages],
            ["첫 질문", "첫 답변", "두번째 질문"],
        )

    def test_unknown_conversation_id_returns_404(self):
        with patch("backend.routers.chat.generate_chat_reply", return_value="답변"):
            response = self.client.post(
                "/api/chat", json={"message": "질문", "conversation_id": "없는대화"}
            )

        self.assertEqual(response.status_code, 404)

    def test_ai_failure_returns_502_without_leaking_the_key(self):
        secret = "sk-this-must-never-appear"
        with patch(
            "backend.routers.chat.generate_chat_reply",
            side_effect=RuntimeError(f"401 unauthorized for {secret}"),
        ):
            response = self.client.post("/api/chat", json={"message": "질문"})

        self.assertEqual(response.status_code, 502)
        self.assertNotIn(secret, response.text)

    def test_ai_failure_does_not_save_a_conversation(self):
        with patch(
            "backend.routers.chat.generate_chat_reply", side_effect=RuntimeError("실패")
        ):
            self.client.post("/api/chat", json={"message": "질문"})

        self.assertEqual(self.fake_client.collection("conversations").documents, {})

    def test_empty_message_is_rejected(self):
        self.assertEqual(
            self.client.post("/api/chat", json={"message": ""}).status_code, 422
        )


if __name__ == "__main__":
    unittest.main()
