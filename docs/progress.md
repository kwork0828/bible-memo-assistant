# 영어성경 암송 AI 비서 — 진행상황

## 1. 현재 환경

- OS: Windows 11
- Terminal: Windows Terminal / PowerShell
- Python: 집 PC 3.13.15, 노트북 3.14.7에서 필수 패키지 import 확인
- Git / GitHub 사용 중
- 현재 작업 브랜치: `feat/data`
- GitHub 저장소: `kwork0828/bible-memo-assistant`
- 저장소 공개 여부: Public

---

## 2. 완료된 작업

### 환경 및 Git

- 프로젝트 폴더 및 Git 저장소 초기화
- `feat/setup`, `feat/api`, `feat/firebase`, `feat/data` 브랜치 구성
- `.venv`, `.gitignore`, `AGENTS.md`, `docs/progress.md` 구성
- GitHub Public 저장소 및 `origin` 연결
- `.env`, `.venv`, Firebase 서비스 계정 키 Git 제외 규칙 확인

### Python 환경

- 필수 패키지 설치
  - fastapi
  - uvicorn
  - firebase-admin
  - openai
  - python-dotenv
- `backend/requirements.txt` 생성
- `backend/.env.example` 생성 및 Firebase/AI 환경변수 예시 정리

### 영어성경 암송 일정 생성

- `scripts/verses.txt` 생성
- World English Bible(WEB) 개발 테스트 구절 5개 준비
- `scripts/make_schedule.py` 생성
- D+0 / D+1 / D+3 / D+7 / D+14 / D+30 복습 일정 구현
- 날짜별 `date`, `value`, `memo` 데이터 생성
- 신규 학습과 복습 데이터 분리
- 100개 미만 데이터 경고 구현
- Python 3.13.15에서 문법 검사 및 실행 성공

### FastAPI 기본 서버

- `backend/main.py` 생성
- FastAPI 애플리케이션 생성
- `GET /`, `GET /health` 구현
- CORSMiddleware 적용
- Swagger `/docs`, `/openapi.json` 정상 동작 확인
- CORS 허용 주소를 환경변수 `ALLOWED_ORIGINS`에서 읽도록 변경

### Firebase / Firestore

- Firebase 프로젝트 `bible-memo-assistant` 생성
- Cloud Firestore `(default)` 데이터베이스 생성
- 위치: `asia-northeast3 (Seoul)`
- 프로덕션 모드로 생성
- 실제 서비스 계정 키는 로컬 PC에만 저장하고 GitHub에는 올리지 않음
- `backend/config.py` 생성
  - `backend/.env` 로드
  - Firebase / CORS / AI 환경변수 중앙 관리
  - 여러 Origin을 쉼표로 받을 수 있도록 구성
- `backend/firebase_client.py` 생성
  - Firebase Admin SDK lazy initialization
  - 공개 API `firebase_admin.get_app()`을 사용해 중복 초기화 방지
  - 로컬 서비스 계정 JSON 파일 경로 지원
  - 배포용 서비스 계정 JSON 문자열 지원
  - 누락/잘못된 설정에 명확한 오류 메시지 제공
- `scripts/setup_local_firebase_env.py` 생성
  - Firebase 키와 `.env`의 Git 제외 여부를 먼저 확인
  - 안전할 때만 로컬 `.env`의 Firebase 경로와 CORS 값을 설정
- `scripts/check_firebase.py` 생성
  - 실제 연결 후 컬렉션 목록만 읽는 읽기 전용 연결 점검 스크립트

### 데이터 API 코드 준비

- `backend/models.py` 생성
  - `date`, `value`, `memo` 시계열 데이터 모델 정의
  - `date`는 `YYYY-MM-DD` 형식 검증
  - `value`는 0 이상으로 검증
- `backend/services/summary.py` 생성
  - 데이터 건수, 기간, 총합, 평균, 최소/최대 요약
- `backend/routers/data.py` 생성
  - POST `/api/data`
  - GET `/api/data`
  - PUT `/api/data/{document_id}`
  - DELETE `/api/data/{document_id}`
  - GET `/api/data/summary`
- `backend/main.py`에 data router 등록
- `scripts/check_data_api_structure.py` 생성
  - Firebase 인증 없이 필수 라우트, 데이터 모델, 요약 로직 구조 점검
- 데이터 API 관련 Python 소스 정적 문법 검사 완료

---

## 3. 보안 상태

GitHub에 올리지 않는 항목:

- `.env`
- `.venv`
- `backend/firebase-service-account.json`
- 실제 OpenAI / 교육기관 API 키
- 실제 Firebase 서비스 계정 JSON 내용

서비스 계정 키는 코드나 채팅에 붙여넣지 않는다.
로컬에서는 `backend/firebase-service-account.json` 파일을 사용하고, 배포 환경에서는 환경변수의 JSON 문자열 방식을 사용할 수 있다.

---

## 4. 현재 검증 상태

완료 증거:

- 일정 생성 기능은 로컬 실행 검증 완료
- FastAPI `/`, `/health`, `/docs`는 브라우저 실행 검증 완료
- Firebase 연결 및 data CRUD API는 코드 준비 완료

아직 남은 실제 검증:

1. 개인 PC에서 `scripts/setup_local_firebase_env.py` 실행
2. `scripts/check_firebase.py`로 실제 Firestore 읽기 연결 확인
3. `scripts/check_data_api_structure.py` 실행
4. Swagger에서 data CRUD를 실제 Firestore에 생성/조회/수정/삭제 테스트

실제 연결과 CRUD 테스트 전까지 Firebase/data API 단계는 최종 완료로 판정하지 않는다.

---

## 5. AI API 방향

- OpenAI-compatible 구조 유지
- 특정 AI 제공자에 종속되지 않도록 구성
- `AI_PROVIDER`, `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL` 환경변수 사용 예정
- 모델명은 추측하지 않고 실제 `/v1/models` 응답 후 선택
- 출력 토큰 제한, 실패 재시도, 로그 기록을 기본 정책으로 적용 예정

---

## 6. 데이터 전략

- 개발 단계에서는 5개 WEB 구절로 파이프라인 검증 완료
- 최종 제출 전 최소 100개 이상의 시계열 데이터 포인트 확보
- `make_schedule.py`는 100개 미만이면 경고하되 개발 테스트는 계속 진행

---

## 7. 다음 개발 작업

실제 Firebase 연결 및 data CRUD 검증 후 다음 순서로 진행한다.

1. 대화 API 구현
2. AI 채팅 및 데이터 요약 컨텍스트 연결
3. Render 배포
4. HTML/CSS/JavaScript 프론트엔드 구현
5. Vercel 배포
6. 100개 이상 데이터 확장 및 최종 검증
7. README / 캡처 / 제출 문서 정리

---

## 8. AI 작업 방식

- GitHub를 실제 상태의 기준으로 사용
- 구현은 한 기능 단위로 진행
- 완료는 모델의 말이 아니라 파일, diff, 실행 결과, 테스트 근거로 판단
- 비밀키 생성, 배포 공개, `main` 병합, 삭제 등 되돌리기 어려운 작업은 사용자 승인 후 진행
- Blocker 또는 Major 문제가 남아 있으면 다음 단계로 넘어가지 않음
