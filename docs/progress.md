# 영어성경 암송 AI 비서 — 진행상황

## 1. 현재 환경

- OS: Windows 11
- Terminal: Windows Terminal / PowerShell
- Python: 집 PC 3.13.15, 노트북 3.14.7에서 필수 패키지 import 확인
- Git / GitHub 사용 중
- 통합 기준 브랜치: `main` (2026-09-18부터, GitHub Default Branch도 `main`)
- GitHub 저장소: `kwork0828/bible-memo-assistant`
- 저장소 공개 여부: Public

---

## 2. 완료·구현 상태

### 1단계 환경 및 Git — 검증 완료

- 프로젝트 폴더 및 Git 저장소 초기화
- `feat/setup`, `feat/api`, `feat/firebase`, `feat/firestore-api`, `feat/ai-chat`, `feat/frontend` 브랜치 구성
- `.venv`, `.gitignore`, `AGENTS.md`, `docs/progress.md` 구성
- GitHub Public 저장소 및 `origin` 연결
- `.env`, `.venv`, Firebase 서비스 계정 키 Git 제외 규칙 확인

### 2단계 암송 일정 생성 — 로컬 검증 완료

- `scripts/verses.txt` 생성
- World English Bible(WEB) 개발 테스트 구절 5개 준비
- `scripts/make_schedule.py` 생성
- D+0 / D+1 / D+3 / D+7 / D+14 / D+30 복습 일정 구현
- 날짜별 `date`, `value`, `memo` 데이터 생성
- 신규 학습과 복습 데이터 분리
- 100개 미만 데이터 경고 구현
- Python 3.13.15에서 문법 검사 및 실행 성공
- 현재 5개 구절 테스트에서는 100개 이상 최종 제출 데이터 요건은 아직 미충족

### 3단계 FastAPI 기본 서버 — 로컬 검증 완료

- `backend/main.py` 생성
- FastAPI 애플리케이션 생성
- `GET /`, `GET /health` 구현
- CORSMiddleware 적용
- Swagger `/docs`, `/openapi.json` 정상 동작 확인
- CORS 허용 주소를 환경변수 `ALLOWED_ORIGINS`에서 읽도록 변경

### 4단계 Firebase / Firestore — 코드 준비 완료, 실제 연결 재검증 필요

- Firebase 프로젝트 `bible-memo-assistant` 생성
- Cloud Firestore `(default)` 데이터베이스 생성
- 위치: `asia-northeast3 (Seoul)`
- 프로덕션 모드로 생성
- Firebase 서비스 계정 키는 개인 PC의 `backend/firebase-service-account.json`에 저장
- `backend/config.py` 생성
  - `backend/.env` 로드
  - Firebase / CORS / AI 환경변수 중앙 관리
- `backend/firebase_client.py` 생성
  - Firebase Admin SDK lazy initialization
  - 공개 API `firebase_admin.get_app()`으로 중복 초기화 방지
  - 로컬 JSON 파일 경로와 배포용 JSON 문자열 모두 지원
- `scripts/setup_local_firebase_env.py` 생성
  - 비밀 파일 Git 제외 여부를 먼저 확인한 뒤 로컬 `.env`를 안전하게 준비
- `scripts/check_firebase.py` 생성
  - 실제 Firestore 컬렉션 목록을 읽기 전용으로 확인
- 남은 검증: 개인 PC에서 `LOCAL_FIREBASE_ENV_OK`, `FIREBASE_CONNECTION_OK` 확인

### 5단계 data API — 구현 완료, 실제 Firestore 통합 테스트 필요

- `backend/models.py`에 data 요청 모델 구현
- `backend/routers/data.py` 구현
  - POST `/api/data`
  - GET `/api/data`
  - PUT `/api/data/{item_id}`
  - DELETE `/api/data/{item_id}`
  - GET `/api/data/summary`
- `backend/services/summary.py` 구현
  - 데이터 수
  - 총 value
  - 평균 value
  - 첫 날짜 / 마지막 날짜
- Firestore 연결 실패 시 비밀정보를 노출하지 않는 503 응답 구조 적용

### 6단계 conversations API — 구현 완료, 실제 Firestore 통합 테스트 필요

- POST `/api/conversations`
- GET `/api/conversations`
- GET `/api/conversations/{conversation_id}`
- DELETE `/api/conversations/{conversation_id}`
- user / assistant 역할만 저장 가능하도록 제한
- 최근 수정 순으로 대화 목록 반환

### 7단계 AI chat — 구현 완료, 실제 Provider 검증 필요

- `backend/services/openai_client.py` 구현
  - OpenAI-compatible Provider 구조
  - `OPENAI_BASE_URL` 선택 적용
  - 모델명을 코드에 하드코딩하지 않음
  - 실제 `OPENAI_MODEL` 환경변수만 사용
  - 출력 토큰 제한
  - 제한된 재시도와 로그
  - JSON 응답 강제 요청
  - ```json 코드 펜스 제거
  - thought / thinking / reasoning / analysis 필드 제거
- `scripts/list_ai_models.py` 구현
  - 실제 Provider의 모델 목록을 먼저 조회
- POST `/api/chat` 구현
  - Firestore data 요약 조회
  - 요약을 시스템 프롬프트에 주입
  - AI 응답 생성
  - conversations에 사용자/AI 메시지 저장
- 남은 검증
  - 교육기관 API 사용 허용 여부 확인
  - 실제 `/v1/models` 결과 확인
  - 실제 존재하는 모델명을 `OPENAI_MODEL`에 설정
  - JSON mode 및 `max_tokens` 호환성 실제 테스트

### 8단계 Render 배포 — 설정 파일 준비 완료, 실제 배포는 미진행

- 저장소 루트에 `render.yaml` 추가(2026-09-18)
- 시작 명령 `python -m uvicorn backend.main:app --host 0.0.0.0 --port
  $PORT`이 실제로 기동해 `/health`가 200을 반환하는 것까지 확인
- API 키, Firebase 서비스 계정 값은 `sync: false`로 표시해 저장소에
  값을 남기지 않고 Render 대시보드에서 직접 입력하도록 함
- 절차는 `docs/deploy.md` 1·3단계 참고
- 실제 외부 공개 배포(Render 계정 연결, Deploy 클릭)는 승인 게이트로
  남겨둠. 계정 로그인이 필요해 AI가 대신할 수 없음
- Firebase/AI 실제 연결 검증 후 진행

### 9단계 Vanilla Frontend — 구현 완료, 브라우저 통합 테스트 필요

- `frontend/admin.html` (이전 `index.html`)
- `frontend/style.css`
- `frontend/admin.js` (이전 `app.js`)
- `frontend/index.html`은 VerseMate 사용자 화면으로 교체됨 (`app.js`, `styles.css`, `library.css`, `routine.css`)
- React/Vue 없이 HTML/CSS/JavaScript만 사용
- 구현 기능
  - Backend API 주소 저장
  - 데이터 요약 카드
  - data 추가/목록/수정/삭제
  - 삭제 전 사용자 재확인
  - AI 채팅 및 로딩 상태
  - 새 대화
  - 이전 대화 목록/불러오기/삭제
  - 모바일 반응형 레이아웃
- 사용자 데이터를 DOM에 넣을 때 `textContent`를 사용해 단순 HTML 삽입을 피함
- 남은 검증: 실제 FastAPI와 브라우저 연결 후 전체 흐름 확인

### 10단계 Vercel 배포 — 설정 파일 준비 완료, 실제 배포는 미진행

- 저장소 루트에 `vercel.json` 추가(2026-09-18). `outputDirectory:
  frontend`로 지정해 별도 빌드 명령 없이 `frontend/` 폴더를 정적
  사이트로 서비스하도록 함
- 절차는 `docs/deploy.md` 2단계 참고
- 실제 Vercel 계정 연결과 Deploy 클릭은 승인 게이트로 남겨둠
- Frontend 로컬 통합 테스트 이후 공개 배포 예정

### 11단계 README / 캡처 / 제출 — 일부만 준비

- `docs/progress.md`로 개발 진행상황 기록 중
- 최종 README, 캡처, 요건 체크리스트는 미완료

---

## 3. 현재 브랜치 흐름

2026-09-10 ~ 09-14 사이에 `feat/setup` → `feat/api`에서 두 갈래로 갈라져
같은 백엔드(data/conversations/chat API)가 서로 다른 구현으로 두 번
만들어졌다. 그중 한 갈래(`feat/firestore-api` → `feat/ai-chat` →
`feat/frontend`)가 가장 완성도가 높았고, 별도로 `feat/firebase`가
VerseMate 사용자 화면을 만들었다.

2026-09-18에 `feat/frontend`를 기준으로 `main`을 새로 만들고,
`feat/firebase`의 화면과 테스트를 그 위로 옮겨 합쳤다. **지금부터는
`main`이 유일한 통합 기준이다.**

원인이 됐던 문제 두 가지(GitHub Default Branch가 `feat/setup`이었던 점,
feat/ 브랜치를 다시 합치는 규칙이 없었던 점)는 AGENTS.md 6조에 반영했다.

과거에 갈라졌던 브랜치 8개(`feat/setup`, `feat/api`, `feat/data`,
`feat/conversations`, `feat/chat`, `feat/firestore-api`, `feat/ai-chat`,
`feat/frontend`)는 삭제 대상이었다. 이 작업 환경의 GitHub 자격증명에는
브랜치 삭제 권한이 없어(push 시 403) AI가 대신 삭제할 수 없었고,
사용자가 GitHub 웹에서 직접 8개를 모두 삭제했다(2026-09-18 완료).

GitHub Default Branch도 같은 날 `main`으로 변경 완료했다. 지금 GitHub에
남은 브랜치는 `main`, `feat/firebase`(원본 커밋 이력 보존 목적으로
의도적으로 유지), `claude/fervent-keller-0biri0`(세션 작업 브랜치)
3개뿐이다.

---

## 4. 보안 상태

GitHub에 올리지 않는 항목:

- `.env`
- `.venv`
- `backend/firebase-service-account.json`
- 실제 OpenAI / 교육기관 API 키
- 실제 Firebase 서비스 계정 JSON 내용

원칙:

- 실제 키 값은 코드, GitHub, 채팅, 캡처에 넣지 않는다.
- 외부 삭제 작업은 프론트엔드에서도 사용자 확인 후 실행한다.
- Firebase/AI 내부 오류 원문은 사용자 응답에 불필요하게 노출하지 않는다.
- 실제 배포와 `main` 병합은 별도 승인 후 진행한다.

---

## 5. 현재 Blocker / Major / Normal

### Blocker

- 없음. 비밀키는 저장소에 넣지 않는 구조로 유지 중.

### Major

1. 실제 로컬 Firebase 인증 연결 결과가 아직 이 문서에 기록되지 않음.
2. data / conversations CRUD를 실제 Firestore에 쓰고 읽는 통합 테스트 미실시.
3. AI Provider의 실제 모델 목록 및 chat 호출 미검증.
4. Frontend ↔ FastAPI ↔ Firestore ↔ AI 전체 흐름 미검증.

Major가 남아 있으므로 구현 코드는 많이 진행됐지만 아직 최종 완료 판정은 하지 않는다.

### Normal

- Render/Vercel 실제 배포 (설정 파일은 준비 완료, `docs/deploy.md` 참고)
- 100개 이상 최종 데이터 확장
- README / 캡처 / 발표 문서

### 완료된 항목 (참고용)

- 과거 중복 브랜치 8개 삭제, Default Branch를 `main`으로 변경
  (2026-09-18)
- `make_schedule.py` 검증 기준을 구절 수 → 날짜 문서 수로 수정
- `scripts/check_api_routes.py`가 FastAPI 0.141의 내부 라우트 표현
  방식 때문에 아무 라우트도 못 찾던 버그 수정 (`app.openapi()` 기준으로
  변경)
- `render.yaml`, `vercel.json`, `docs/deploy.md` 추가

---

## 6. 다음에 개인 PC에서 가장 먼저 할 검증

1. 최신 `main` 받기 (`feat/frontend`가 아니라 `main`)
2. `scripts/setup_local_firebase_env.py` 실행
3. `scripts/check_firebase.py` 실행
4. `scripts/check_api_routes.py` 실행
5. Uvicorn 실행 후 Swagger에서 data / conversations 실제 CRUD 테스트
6. 실제 Provider 정보가 준비되면 `scripts/list_ai_models.py` 실행
7. 실제 존재 모델 설정 후 `/api/chat` 한 건 테스트
8. `frontend/index.html`(사용자 화면)과 `frontend/admin.html`(데이터
   관리 화면)을 브라우저에서 열고 전체 흐름 확인

---

## 7. 진행률 해석

- 코드 구현량 기준: 약 75% 수준 (브랜치 통합, 화면 합류, 테스트 53개로
  증가했으나 새 기능이 늘어난 것은 아니다)
- 실제 검증·배포·제출까지 포함한 완성도 기준: 약 55~60% 수준
  (Blocker/Major는 그대로 남아 있다)

구현량과 완료 판정을 구분한다. 모델이나 문서의 “완료” 주장보다 실제 실행 증거를 우선한다.
브랜치가 하나로 합쳐졌다고 해서 Firebase/AI 실연결 검증까지 끝난 것은 아니다.

---

## 8. 다음 개발 순서

1. 실제 Firebase 연결 및 CRUD 통합 검증 (본인 PC, `docs/deploy.md`
   "로컬에서 미리 검증하고 싶다면" 참고)
2. AI 모델 목록 조회 및 chat 실호출 검증 (본인 PC)
3. Frontend 전체 흐름 검증 (index.html, admin.html 둘 다)
4. Render 배포 (`render.yaml` 준비 완료, `docs/deploy.md` 1·3단계)
5. Vercel 배포 (`vercel.json` 준비 완료, `docs/deploy.md` 2단계)
6. 100개 이상 시계열 데이터 확장 (구절 70개 이상이면 날짜 문서 100개 이상)
7. README / 캡처 / 제출 요건 체크

---

## 9. AI 작업 방식

- GitHub를 실제 상태의 기준으로 사용
- 구현은 한 기능 단위로 진행
- 완료는 모델의 말이 아니라 파일, diff, 실행 결과, 테스트 근거로 판단
- 비밀키, 유료 결제, 공개 배포, `main` 병합, 삭제 등 되돌리기 어려운 작업은 사용자 승인 후 진행
- Blocker 또는 Major 문제가 남아 있으면 최종 완료로 판정하지 않음
