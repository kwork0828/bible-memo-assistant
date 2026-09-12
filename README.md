# Bible Memo Assistant

영어성경 암송 일정을 시계열 데이터로 관리하고, 학습 부담 요약을 AI에게 전달해 암송 코칭 대화를 제공하는 개인 프로젝트입니다.

## 주요 기능

- 영어성경 구절 기반 복습 일정 생성
- D+0 / D+1 / D+3 / D+7 / D+14 / D+30 복습 주기
- FastAPI 백엔드
- Cloud Firestore 영구 저장
- 암송 데이터 추가 / 조회 / 수정 / 삭제
- 암송 데이터 요약
- 이전 대화 저장 / 조회 / 삭제
- OpenAI-compatible AI 채팅 구조
- Vanilla HTML / CSS / JavaScript 프론트엔드

## 기술 스택

- Python 3.10+
- FastAPI
- Firebase Admin SDK
- Cloud Firestore
- OpenAI Python SDK
- python-dotenv
- HTML / CSS / JavaScript
- Render 예정
- Vercel 예정

## 프로젝트 구조

```text
bible-memo-assistant/
├─ backend/
│  ├─ main.py
│  ├─ config.py
│  ├─ firebase_client.py
│  ├─ models.py
│  ├─ routers/
│  │  ├─ data.py
│  │  ├─ conversations.py
│  │  └─ chat.py
│  └─ services/
│     ├─ summary.py
│     └─ openai_client.py
├─ frontend/
│  ├─ index.html
│  ├─ style.css
│  └─ app.js
├─ scripts/
│  ├─ make_schedule.py
│  ├─ check_firebase.py
│  ├─ check_api_routes.py
│  └─ list_ai_models.py
├─ docs/
│  ├─ architecture.md
│  ├─ progress.md
│  └─ review-guide.md
└─ AGENTS.md
```

## 보안 원칙

실제 비밀값은 GitHub에 올리지 않습니다.

- `.env`
- `.venv/`
- `backend/firebase-service-account.json`
- 실제 AI API 키
- 실제 Firebase 서비스 계정 JSON 내용

저장소에는 예시 파일인 `backend/.env.example`만 포함합니다.

## AI 모델 선택 원칙

모델명을 코드에 추측해서 넣지 않습니다.

1. Provider API 키 / base URL 설정
2. `scripts/list_ai_models.py` 실행
3. 실제 응답한 모델 ID 확인
4. 그 중 사용할 모델을 `OPENAI_MODEL`에 설정
5. 작은 입력으로 채팅 테스트

## 현재 상태

구현된 코드와 실제 검증 상태를 구분합니다.

- 일정 생성: 로컬 검증 완료
- FastAPI 기본 서버: 로컬 검증 완료
- Firebase 연결 코드: 구현 완료, 실제 인증 연결 재검증 필요
- data API: 구현 완료, 실제 Firestore 통합 테스트 필요
- conversations API: 구현 완료, 실제 Firestore 통합 테스트 필요
- AI chat: 구현 완료, 실제 Provider 모델 조회·호출 테스트 필요
- Frontend: 구현 완료, 실제 백엔드 통합 테스트 필요
- Render / Vercel 배포: 미진행
- 100개 이상 최종 시계열 데이터: 미완료

자세한 진행상황은 `docs/progress.md`, 구조 설명은 `docs/architecture.md`, 검증 순서는 `docs/review-guide.md`를 참고하세요.

## 데이터 전략

개발 초반에는 소수 구절로 전체 흐름을 검증하고, 최종 제출 전 최소 100개 이상의 시계열 데이터 포인트를 확보합니다.

현재 샘플 구절은 저작권 문제가 없는 World English Bible(WEB)을 기준으로 사용합니다.

## 개발 원칙

- 한 기능 단위로 구현
- 실제 실행 결과로 완료 판정
- 비밀값 하드코딩 금지
- 외부 삭제 / 배포 / 병합은 승인 후 실행
- 모델명과 외부 API 동작은 추측하지 않고 실제 응답으로 확인
