# 영어성경 암송 AI 비서 — 진행상황

## 1. 현재 환경

- OS: Windows 11
- Terminal: Windows Terminal
- PowerShell: 7.6.6
- 현재 가상환경 Python: 3.14.7
- Git: 설치 및 사용 중
- GitHub CLI: 설치 및 로그인 완료
- 현재 로컬 작업 브랜치: feat/firebase
- GitHub 저장소: kwork0828/bible-memo-assistant
- 저장소 공개 여부: Public

---

## 2. 완료된 작업

### 환경 및 Git

- 프로젝트 폴더 생성
- Git 저장소 초기화
- feat/setup 브랜치 생성
- feat/api 브랜치 생성
- feat/firebase 브랜치 생성
- Python 가상환경 `.venv` 생성
- `.gitignore` 작성
- `AGENTS.md` 작성
- `docs/progress.md` 작성
- GitHub Public 저장소 생성
- 로컬 저장소와 `origin` 연결
- `feat/setup` 원격 push 완료
- `feat/api` 원격 push 완료

### Python 환경

- 필수 패키지 설치
  - fastapi
  - uvicorn
  - firebase-admin
  - openai
  - python-dotenv
- 현재 가상환경 Python 3.14.7에서 필수 패키지 import 성공
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
- 아직 실제 업무 컬렉션은 생성하지 않음
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
- `scripts/check_firebase.py` 생성
  - 실제 연결 후 컬렉션 목록만 읽는 읽기 전용 연결 점검 스크립트
- Firebase 관련 Python 파일 정적 문법 검사 완료

### Firebase 클라이언트 준비

- `backend/firebase_client.py` 생성
- Render에서는 `FIREBASE_SERVICE_ACCOUNT_JSON` 환경변수에서 서비스 계정 정보 로드
- 로컬에서는 `FIREBASE_SERVICE_ACCOUNT_FILE`에 지정한 Git 제외 키 파일 사용
- `backend/.env`에 비밀값 대신 로컬 키 파일명만 설정
- 서비스 계정 JSON 형식과 필수 항목 검증
- 기본 Firebase 앱 중복 초기화 방지
- Firestore 클라이언트 반환 함수 구현
- 비밀값을 오류 메시지에 출력하지 않도록 예외 처리
- 외부 Firebase 접속 없이 단위 테스트 12개 통과
- Codex 실행 세션에서 일회성 환경변수 주입으로 Firebase 인증과
  Firestore `data` 컬렉션 읽기 성공을 관찰함(당시 문서 0개)
- 2026-09-13에 Git에서 제외된 `backend/firebase-service-account.json`을
  일회성 환경변수로 주입해 실제 연결을 재검증함(문서 0개)

---

## 3. 주요 커밋

- `8a57606` chore: initialize project environment
- `180215f` feat: add memorization schedule generator
- `5195fea` feat: add FastAPI application skeleton
- `d02c7ef` feat: update progress after FastAPI setup
- `46c02ae` feat: add environment configuration module
- `a5f1a84` feat: add lazy Firebase client
- `9feec09` chore: update environment variable example
- `c3041fe` feat: load CORS origins from environment
- `b0afecc` chore: add read-only Firebase connection check

---

## 4. 보안 상태

GitHub에 올리지 않는 항목:

- `.env`
- `.venv`
- `backend/firebase-service-account.json`
- 실제 OpenAI / 교육기관 API 키
- 실제 Firebase 서비스 계정 JSON 내용

커밋 전에는 반드시 다음 순서로 확인한다.

1. 편집기에서 Ctrl+S 저장
2. 실행 중 프로그램 또는 서버 Ctrl+C 종료
3. `git status` 확인
4. `.env`, `.venv`, Firebase 키가 목록에 없는지 확인
5. `python -m unittest discover -s . -p "test_*.py"` 실행 후 실제 테스트 통과 건수 확인 (`Ran 0 tests`는 통과 아님)
6. `git add .`
7. `git commit -m "..."`
8. `git push`
서비스 계정 키는 코드나 채팅에 붙여넣지 않는다.
로컬에서는 `backend/firebase-service-account.json` 파일을 사용하고, 배포 환경에서는 환경변수의 JSON 문자열 방식을 사용할 수 있다.

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

## 7. 현재 상태와 승인 게이트

- 이전 작업 브랜치: `feat/setup`
- 이전 API 작업 브랜치: `feat/api`
- 현재 작업 브랜치: `feat/firebase`
- `feat/firebase`는 FastAPI 기본 서버 작업 완료 커밋에서 분기
- FastAPI 기본 서버 커밋 `5195fea`가 `origin/feat/api`에 push 완료
- Firebase 클라이언트 변경사항은 `feat/firebase` 브랜치에서 작업
현재 Firebase 연결 코드는 GitHub `feat/firebase`에 준비되어 있다.
아직 실제 서비스 계정 비밀키를 저장소에 넣지 않았으며 실제 Firestore 인증 연결은 수행하지 않았다.

다음 외부 변경은 사용자 승인 후 진행한다.

1. Firebase 서비스 계정 비공개 키 생성
2. 개인 PC의 `backend/firebase-service-account.json`에 저장
3. 개인 PC의 `backend/.env` 생성
4. `scripts/check_firebase.py`로 실제 Firestore 읽기 연결 확인

---

## 8. 다음 개발 작업

1. 데이터 API 구현
   - POST /api/data
     - `get_firestore_client()`를 실제로 호출하는 첫 라우트가 된다.
   - GET /api/data
   - PUT /api/data/{id}
   - DELETE /api/data/{id}
   - GET /api/data/summary
2. 대화 API 구현
3. AI 채팅 및 데이터 요약 컨텍스트 연결
4. Render 배포
5. HTML/CSS/JavaScript 프론트엔드 구현
6. Vercel 배포
7. README 및 제출 캡처 정리

---

## 9. AI 작업 방식

Codex에서 이어서 작업할 때는 다음 순서로 진행한다.

1. `AGENTS.md` 전체 확인
2. `docs/progress.md` 전체 확인
3. 현재 브랜치 및 최신 커밋 확인
4. 현재 저장소 구조 확인
5. 다음 기능 하나만 작업
6. 테스트 결과와 수정 파일을 보고
7. GitHub push는 사용자의 로컬 환경에서 최종 확인 후 수행

Firebase 클라이언트 코드, 단위 테스트, 실제 Firestore 읽기 검증이 완료되었다.
다음 개발 단계는 Firestore `data` 컬렉션을 사용하는 데이터 API 구현이다.
- GitHub를 실제 상태의 기준으로 사용
- 구현은 한 기능 단위로 진행
- 완료는 모델의 말이 아니라 파일, diff, 실행 결과, 테스트 근거로 판단
- 비밀키 생성, 배포 공개, `main` 병합, 삭제 등 되돌리기 어려운 작업은 사용자 승인 후 진행
- Blocker 또는 Major 문제가 남아 있으면 다음 단계로 넘어가지 않음
