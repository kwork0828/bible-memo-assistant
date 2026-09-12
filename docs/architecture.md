# Bible Memo Assistant — Architecture

## 1. 한 줄 설명

영어성경 암송 일정을 시계열 데이터로 관리하고, 사용자의 학습 부담 요약을 AI에게 전달해 암송 코칭 대화를 제공하는 FastAPI + Firestore 웹앱이다.

## 2. 전체 흐름

```text
verses.txt
   ↓
make_schedule.py
   ↓
날짜별 암송 일정(date / value / memo)
   ↓
FastAPI data API
   ↓
Cloud Firestore data 컬렉션
   ↓
summary.py가 통계 요약
   ↓
/api/chat 시스템 프롬프트에 요약 주입
   ↓
OpenAI-compatible Provider
   ↓
AI 답변
   ↓
Firestore conversations 컬렉션 저장
   ↓
Vanilla HTML/CSS/JS 화면 표시
```

## 3. 주요 모듈

| 파일 | 역할 | 비유 |
|---|---|---|
| `backend/main.py` | FastAPI 앱과 라우터 등록 | 건물 입구 |
| `backend/config.py` | 환경변수 읽기 | 설정 안내데스크 |
| `backend/firebase_client.py` | Firebase Admin / Firestore 연결 | 데이터 창고 연결 담당 |
| `backend/models.py` | API 입력 형식 검증 | 접수 양식 검사 |
| `backend/routers/data.py` | 암송 데이터 CRUD | 일정 접수 창구 |
| `backend/routers/conversations.py` | 대화 저장·조회·삭제 | 대화 기록 창구 |
| `backend/routers/chat.py` | 데이터 요약 → AI → 대화 저장 | AI 코칭 창구 |
| `backend/services/summary.py` | 시계열 데이터 요약 | 통계 계산 담당 |
| `backend/services/openai_client.py` | AI Provider 호출·파싱·재시도 | 외부 AI 연결 담당 |
| `scripts/make_schedule.py` | 복습 일정 생성 | 학습 일정표 제작기 |
| `scripts/list_ai_models.py` | 실제 모델 목록 조회 | 사용 가능한 모델 확인표 |
| `frontend/*` | 사용자 화면 | 앱의 조작판 |

## 4. Firestore 데이터 구조

### `data`

문서 하나는 날짜별 암송 일정을 뜻한다.

```text
id: Firestore 문서 ID
date: YYYY-MM-DD
value: 해당 날짜의 총 암송 단어 수
memo:
  new: 신규 학습 구절 목록
  review: 복습 구절 목록
created_at: 생성 UTC 시각
updated_at: 수정 UTC 시각
```

`value`는 날짜별 학습 부담을 숫자로 비교하기 위한 값이다.

### `conversations`

```text
id: Firestore 문서 ID
title: 대화 제목
messages:
  - role: user | assistant
    content: 실제 메시지
created_at: 생성 UTC 시각
updated_at: 수정 UTC 시각
```

외부 입력으로 `system` 역할을 저장하지 않는다. 시스템 지시는 서버 내부에서만 만든다.

## 5. 필수 API

### Data

- `POST /api/data`
- `GET /api/data`
- `PUT /api/data/{item_id}`
- `DELETE /api/data/{item_id}`
- `GET /api/data/summary`

### Conversations

- `POST /api/conversations`
- `GET /api/conversations`
- `GET /api/conversations/{conversation_id}`
- `DELETE /api/conversations/{conversation_id}`

### AI

- `POST /api/chat`

## 6. AI 요청 흐름

1. Firestore `data`를 읽는다.
2. `summary.py`에서 데이터 개수, 총/평균 value, 기간을 계산한다.
3. 요약을 서버 내부 시스템 프롬프트에 넣는다.
4. 기존 대화와 새 사용자 메시지를 OpenAI-compatible API에 전달한다.
5. JSON 응답을 요청한다.
6. 코드 펜스가 있으면 제거한다.
7. `thought`, `thinking`, `reasoning`, `analysis` 필드는 사용자 응답에서 제거한다.
8. 최종 `reply`를 Firestore `conversations`에 저장한다.

모델명은 코드에 고정하지 않는다. 먼저 `scripts/list_ai_models.py`로 실제 Provider가 제공하는 모델을 확인한 뒤 `OPENAI_MODEL`에 설정한다.

## 7. 보안 경계

GitHub에 올리지 않는다.

- `backend/.env`
- `.venv/`
- `backend/firebase-service-account.json`
- 실제 API 키
- 실제 Firebase 서비스 계정 JSON 내용

로컬에서는 Firebase JSON 파일 경로를 사용하고, 배포 환경에서는 서비스 계정 JSON 문자열을 환경변수로 전달할 수 있게 구성한다.

브라우저는 Firebase 서비스 계정 키를 알지 못한다. Frontend → FastAPI → Firestore 순서로 요청한다.

## 8. 삭제·외부 변경 원칙

- 프론트엔드 삭제 버튼은 사용자 재확인 후 API를 호출한다.
- 실제 배포, `main` 병합, 비밀키 변경은 별도 승인 게이트로 둔다.
- AI 호출 실패와 Firebase 연결 실패는 사용자 화면에 내부 비밀정보를 그대로 노출하지 않는다.

## 9. 아직 실제 검증이 필요한 부분

현재 코드 구현과 실제 운영 성공을 구분한다.

- 실제 서비스 계정으로 Firestore 연결
- `data` CRUD 실제 읽기/쓰기/수정/삭제
- `conversations` 실제 저장/조회/삭제
- 실제 OpenAI-compatible Provider의 모델 목록 조회
- 실제 선택 모델의 JSON mode / 토큰 파라미터 호환성
- `/api/chat` 전체 흐름
- Frontend ↔ Backend 전체 흐름
- Render / Vercel 공개 배포

위 검증 증거가 나오기 전에는 해당 기능을 최종 완료로 판정하지 않는다.
