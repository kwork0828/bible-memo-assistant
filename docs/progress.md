# 영어성경 암송 AI 비서 — 진행상황

## 1. 현재 환경

- OS: Windows 11
- Terminal: Windows Terminal / PowerShell
- Python: 집 PC 3.13.15, 노트북 3.14.7에서 필수 패키지 import 확인
- Git / GitHub 사용 중
- 현재 작업 브랜치: `feat/chat`
- GitHub 저장소: `kwork0828/bible-memo-assistant`
- 저장소 공개 여부: Public

---

## 2. 완료된 코드 준비

### 환경 및 Git

- `feat/setup`, `feat/api`, `feat/firebase`, `feat/data`, `feat/conversations`, `feat/chat` 브랜치 구성
- `.venv`, `.gitignore`, `AGENTS.md`, `docs/progress.md` 구성
- GitHub Public 저장소 및 `origin` 연결
- `.env`, `.venv`, Firebase 서비스 계정 키 Git 제외 규칙 확인

### 영어성경 암송 일정 생성

- `scripts/verses.txt`에 WEB 개발 테스트 구절 5개 준비
- `scripts/make_schedule.py`에서 D+0 / D+1 / D+3 / D+7 / D+14 / D+30 복습 일정 구현
- 날짜별 `date`, `value`, `memo` 데이터 생성
- 100개 미만 경고 구현
- Python 3.13.15에서 실행 검증 완료

### FastAPI 기본 서버

- `backend/main.py` 생성
- `GET /`, `GET /health` 구현
- CORS 환경변수화
- Swagger `/docs`, `/openapi.json` 로컬 검증 완료

### Firebase / Firestore

- Firebase 프로젝트 `bible-memo-assistant` 생성
- Cloud Firestore `(default)` 데이터베이스 생성
- 위치: `asia-northeast3 (Seoul)`
- 프로덕션 모드로 생성
- 실제 서비스 계정 키는 로컬 PC에만 저장하고 GitHub에는 올리지 않음
- `backend/config.py` 생성
- `backend/firebase_client.py` 생성
  - lazy initialization
  - 중복 초기화 방지
  - 로컬 파일 경로 / 배포용 JSON 문자열 지원
- `scripts/setup_local_firebase_env.py` 생성
- `scripts/check_firebase.py` 생성

### Data API

- `backend/models.py`에 데이터 모델 구현
- `backend/services/summary.py` 구현
- `backend/routers/data.py` 구현
  - POST `/api/data`
  - GET `/api/data`
  - PUT `/api/data/{document_id}`
  - DELETE `/api/data/{document_id}`
  - GET `/api/data/summary`
- `scripts/check_data_api_structure.py` 생성

### Conversation API

- 대화 메시지 / 생성 / 응답 모델 구현
- `backend/routers/conversations.py` 구현
  - POST `/api/conversations`
  - GET `/api/conversations`
  - GET `/api/conversations/{conversation_id}`
  - DELETE `/api/conversations/{conversation_id}`
- `scripts/check_conversation_api_structure.py` 생성

### AI Chat API 코드 준비

- `backend/services/openai_client.py` 생성
  - OpenAI / OpenAI-compatible `base_url` 지원
  - 모델명을 코드에 하드코딩하지 않음
  - `OPENAI_MODEL`이 없으면 명확한 오류
  - 실제 모델 목록 조회 함수 제공
  - 출력 토큰 제한에 `max_completion_tokens` 사용
- `scripts/list_ai_models.py` 생성
  - 실제 API의 모델 목록을 먼저 조회하도록 구성
- `backend/routers/chat.py` 구현
  - POST `/api/chat`
  - Firestore `data` 요약을 시스템 프롬프트에 주입
  - 기존 대화 이력 일부를 컨텍스트로 사용
  - AI 응답 성공 후 `conversations` 컬렉션에 저장
  - 실패 시 내부 오류 세부정보를 사용자 응답에 노출하지 않음
- `scripts/check_chat_api_structure.py` 생성

---

## 3. 보안 상태

GitHub에 올리지 않는 항목:

- `.env`
- `.venv`
- `backend/firebase-service-account.json`
- 실제 AI API 키
- 실제 Firebase 서비스 계정 JSON 내용

비밀값은 코드나 채팅에 붙여넣지 않는다.
배포 전에는 Render 환경변수 방식으로 전환한다.

---

## 4. 검증 상태

### 실제 실행 검증 완료

- 암송 일정 생성
- FastAPI `/`, `/health`, `/docs`

### 코드 준비 완료, 실제 연결 검증 대기

- Firebase 인증 연결
- Data CRUD API
- Conversation API
- AI 모델 목록 조회
- AI Chat API

실제 연결 전까지 위 단계는 최종 완료로 판정하지 않는다.

개인 PC에서 다음 순서로 검증한다.

1. `scripts/setup_local_firebase_env.py`
2. `scripts/check_firebase.py`
3. `scripts/check_data_api_structure.py`
4. `scripts/check_conversation_api_structure.py`
5. `scripts/check_chat_api_structure.py`
6. Swagger에서 Data / Conversation CRUD 실제 검증
7. 허용된 AI API 키와 Base URL 설정
8. `scripts/list_ai_models.py`로 실제 모델 목록 조회
9. 실제 목록에 존재하는 모델만 `OPENAI_MODEL`에 설정
10. POST `/api/chat` 실제 호출 검증

---

## 5. 다음 개발 작업

실제 Firebase / AI 연결 검증 후 다음 순서로 진행한다.

1. Render 백엔드 배포
2. HTML/CSS/JavaScript 프론트엔드 구현
3. Vercel 프론트엔드 배포
4. 100개 이상 시계열 데이터 확장 및 최종 검증
5. README / 캡처 / 제출 문서 정리

---

## 6. AI 작업 방식

- GitHub를 실제 상태의 기준으로 사용
- 구현과 검증을 분리
- 완료는 모델의 말이 아니라 파일, diff, 실행 결과, 테스트 근거로 판단
- 비밀키 생성, 배포 공개, `main` 병합, 삭제 등 되돌리기 어려운 작업은 사용자 승인 후 진행
- Blocker 또는 Major 문제가 남아 있으면 다음 단계로 넘어가지 않음
