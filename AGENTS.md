# 영어성경 암송 AI 비서 — Codex 작업 지침

## 1. 프로젝트 목표

이 프로젝트는 영어성경 암송 일정을 시계열 데이터로 관리하고, 사용자의 암송 진도와 학습 부담을 이해하는 AI 비서를 만드는 개인 학습 프로젝트다.

최종 결과물은 다음 기술 스택을 사용한다.

* Backend: FastAPI
* Database: Firebase Firestore
* AI: OpenAI-compatible API 구조
* Frontend: HTML / CSS / JavaScript
* Backend Deploy: Render
* Frontend Deploy: Vercel
* Python: 3.10 이상
* 현재 로컬 Python: 3.13.15

프론트엔드는 React, Vue 등 프레임워크를 사용하지 않는다.

---

## 2. 사용자의 개발 수준

사용자는 프로그래밍 입문자다.

코드를 직접 작성하기보다 완성된 코드를 복사하여 실행하고, 그 의미를 이해하면서 진행하는 방식을 선호한다.

설명할 때는 전문용어를 먼저 쉬운 일상 비유로 설명하고 그다음 기술적 의미를 설명한다.

작업을 한꺼번에 많이 진행하지 않는다.

기본 진행 단위는 3개 작업이다.

---

## 3. Codex 작업 원칙

한 번에 하나의 기능 단위만 작업한다.

여러 파일을 수정해야 한다면 작업 전에 다음을 먼저 설명한다.

1. 어떤 파일을 수정하는지
2. 각각 왜 수정하는지
3. 수정 후 무엇을 확인할지

사용자가 요청하지 않은 대규모 리팩터링을 하지 않는다.

현재 동작하는 구조를 임의로 변경하지 않는다.

새 라이브러리를 추가하기 전에 기존 과제 기술 스택으로 해결할 수 있는지 먼저 검토한다.

불확실한 내용은 추측하지 않는다.

확인이 필요한 경우 확인 명령이나 문서를 먼저 제시한다.

---

## 4. 사용자 환경

* Windows 11
* Windows Terminal
* PowerShell 7
* Oh My Posh
* Python 3.13.15
* Git
* GitHub
* 작업 경로:
  C:\Users\user\Documents\bible-memo-assistant

VS Code 탐색기가 정상적으로 동작하지 않을 수 있으므로 파일 생성 안내에서 VS Code 탐색기를 전제로 하지 않는다.

파일을 사용자가 직접 만들 때는 기본적으로 다음 방식을 사용한다.

* PowerShell New-Item
* notepad
* 붙여넣기
* Ctrl+S

---

## 5. 명령 안내 방식

사용자가 실제로 실행해야 하는 터미널 명령만 코드 블록으로 표시한다.

설명, 예상 출력, 파일 구조, 참고 예시는 코드 블록으로 표시하지 않는다.

사용자가 코드 블록의 복사 버튼을 실수로 눌러 명령처럼 실행할 수 있기 때문이다.

PowerShell 명령은 한 줄씩 제공한다.

PowerShell에서 && 로 여러 명령을 이어붙이지 않는다.

페이저가 열릴 수 있는 Git 명령은 --no-pager 옵션을 사용한다.

실행 중 프로그램이나 서버를 종료할 때는 창을 닫지 않고 Ctrl+C를 사용하도록 안내한다.

---

## 6. Git 브랜치

이 프로젝트는 개인 프로젝트다.

feat/ 접두어는 Git의 필수 규칙이 아니라 관리 편의를 위한 관례다.

현재는 feat/ 규칙을 사용한다.

예:

* feat/data
* feat/chat

main 브랜치에는 직접 개발하지 않는다.

**중요: feat/ 브랜치는 반드시 main에서 분기하고, 작업이 끝나면 main으로 다시 합친다.**

2026-09 중순까지는 이 규칙이 지켜지지 않아 feat/setup, feat/api, feat/data,
feat/conversations, feat/chat, feat/firestore-api, feat/ai-chat, feat/frontend,
feat/firebase까지 브랜치 9개가 서로 합쳐지지 않은 채 각자 갈라져 나갔다.
그 결과 같은 백엔드(API)가 세 번 따로 구현됐다.

원인은 다음 두 가지였다.

1. GitHub 저장소의 Default Branch가 한동안 main이 아니라 feat/setup으로
   설정돼 있었다. 새 세션이 저장소를 열 때마다 커밋 4개짜리 가장 이른
   상태에서 시작했다.
2. "main에는 직접 개발하지 않는다"는 규칙만 있고 "다시 합친다"는 규칙이
   없어서, 각 세션이 새 feat/ 브랜치를 만들고 끝내는 지점에서 멈췄다.

2026-09-18에 feat/frontend를 기준으로 main을 새로 만들고
(feat/firebase의 화면은 그 위에 옮겨 합쳤다), GitHub Default Branch도
main으로 바꿨다. 이제부터 다음을 지킨다.

* 새 세션은 항상 origin/main에서 새 feat/ 브랜치를 만든다.
* 작업이 끝나면 그 브랜치를 main에 병합(merge 또는 PR)하고, 병합이
  끝난 브랜치는 삭제한다.
* main에서 벗어난 채로 다음 세션까지 남겨두지 않는다.

---

## 7. Git 커밋 전 필수 보안 절차

커밋을 안내할 때는 반드시 다음 순서를 사용한다.

1. 메모장 또는 편집기에서 Ctrl+S 저장 여부 확인
2. 실행 중인 Python 프로그램이나 서버가 있다면 Ctrl+C로 종료
3. git status 실행
4. .env, .venv, Firebase 서비스 계정 키가 Git 목록에 없는지 확인
5. git add .
6. git commit -m "..."
7. git push

특히 git status 보안 검사를 생략하지 않는다.

커밋 메시지 접두어는 다음을 사용한다.

* feat
* fix
* docs
* chore

---

## 8. Git에 올라가면 안 되는 파일

.gitignore에는 최소 다음이 포함되어야 한다.

* .venv/
* **pycache**/
* *.pyc
* .env
* backend/firebase-service-account.json
* .DS_Store

*.json 전체를 무시하지 않는다.

일반 설정 JSON이나 샘플 JSON까지 Git에서 제외될 수 있기 때문이다.

Firebase 서비스 계정 파일은 정확한 파일명으로만 제외한다.

---

## 9. Python 환경

현재 Python은 3.13.15다.

가상환경 .venv를 사용한다.

필수 패키지는 다음과 같다.

* fastapi
* uvicorn
* firebase-admin
* openai
* python-dotenv

Python 3.13에서 패키지 설치와 import를 실제로 검증한 뒤 진행한다.

패키지 호환 문제가 실제로 확인되기 전에는 임의로 Python 3.12로 낮추지 않는다.

필요한 경우에만 Python 3.12 우회를 제안한다.

---

## 10. 데이터 전략

최종 과제는 최소 100개 이상의 시계열 데이터 포인트를 요구한다.

하지만 개발 초반에는 현재 준비된 소수의 영어성경 구절로 파이프라인을 먼저 검증한다.

권장 순서:

소수 구절 테스트
→ 일정 생성 검증
→ 날짜 및 복습 계산 검증
→ 구조 확정
→ 100절 이상 확장
→ 최종 100개 이상 데이터 생성

scripts/make_schedule.py에는 반드시 생성된 시계열 데이터 포인트
(날짜 문서) 개수 검증을 넣는다. 구절 개수가 아니다.

복습 간격(D+0~D+30)이 곱해지기 때문에 구절 개수와 날짜 문서 개수는
다르다. 예를 들어 구절 70개면 날짜 문서는 100개를 넘는다.

날짜 문서가 100개 미만이면 프로그램을 무조건 중단시키지는 않는다.

개발 테스트가 가능하도록 실행하되 다음 의미의 경고를 출력한다.

"현재 생성된 데이터 포인트 수는 과제 제출 기준인 100개 미만이며 개발 테스트용 데이터입니다."

최종 제출 전에는 데이터 포인트가 100개 이상인지 반드시 검증한다.

---

## 11. 암송 복습 일정

기본 복습 간격은 다음을 사용한다.

* D+0 신규 학습
* D+1 1차 복습
* D+3 2차 복습
* D+7 3차 복습
* D+14 4차 복습
* D+30 5차 복습

Firestore data 컬렉션의 문서 하나는 하루 암송 일정을 의미한다.

핵심 데이터는 다음 의미를 갖는다.

* date: 날짜
* value: 해당 날짜에 암송할 총 단어 수
* memo: 신규 및 복습 구절 정보

value는 해당 날짜의 학습 부담을 수치화하기 위한 값이다.

---

## 12. 성경 본문

공개 서비스에서는 저작권 문제가 없는 성경 번역을 사용한다.

현재 기본 방향은 World English Bible(WEB)이다.

저작권이 있는 번역본을 임의로 프로젝트 데이터에 삽입하지 않는다.

---

## 13. AI Provider 설계

AI 호출 코드는 특정 업체에 종속되지 않도록 만든다.

앱의 데이터 처리, Firestore, 채팅 저장 기능과 AI Provider를 분리한다.

AI 호출 로직은 services 계층의 한 곳에 모은다.

예상 구조:

backend/config.py
backend/services/openai_client.py

환경변수를 통해 Provider를 교체할 수 있게 설계한다.

예상 환경변수:

AI_PROVIDER
OPENAI_API_KEY
OPENAI_BASE_URL
OPENAI_MODEL

API 키와 모델명을 소스 코드에 하드코딩하지 않는다.

현재 교육기관에서 제공하는 OpenAI-compatible API의 활용 가능성을 검토하고 있다.

교육과정 종료, 정책 변경, 이용자 증가, 한도 문제 등이 발생하면 개인 OpenAI API로 쉽게 교체할 수 있어야 한다.

Provider 변경 때문에 라우터, Firestore, 프론트엔드 등을 수정해야 하는 구조로 만들지 않는다.

---

## 14. AI 모델명 검증

AI 모델명을 절대 추측하지 않는다.

코드에 임의로 gpt-* 모델명을 입력하지 않는다.

항상 다음 순서로 진행한다.

1. 실제 API의 모델 목록 조회
2. 사용 가능한 모델 결과 확인
3. 그 결과에 존재하는 모델 선택
4. OPENAI_MODEL 환경변수에 입력
5. 작은 테스트 호출
6. 프로젝트 연결

없는 모델명을 추측해서 발생하는 404 오류를 방지하는 것이 목적이다.

---

## 15. API 키 보안

실제 API 키 값은 코드, 문서, GitHub, 채팅에 출력하지 않는다.

안내 예시는 반드시 다음과 같이 표시한다.

OPENAI_API_KEY=여기에 본인 키

실제 값은 .env 또는 Render 환경변수에만 저장한다.

저장소에는 .env.example만 올린다.

---

## 16. AI 비용 통제

AI 요청에는 반드시 출력 토큰 제한을 적용한다.

사용하는 OpenAI SDK/API 버전에 맞는 실제 파라미터를 확인하고 적용한다.

과도한 출력이나 반복 호출을 피한다.

개발 단계에서는 작은 입력으로 먼저 테스트한다.

API 실패에는 예외 처리와 로그를 넣는다.

---

## 17. FastAPI 구조

단일 파일에 모든 코드를 몰아넣지 않는다.

예상 구조:

backend/

* main.py
* config.py
* firebase_client.py
* models.py

backend/routers/

* data.py
* conversations.py
* chat.py

backend/services/

* summary.py
* openai_client.py

routers는 HTTP 요청을 받는 접수창구 역할을 한다.

services는 계산, 요약, AI 호출 등 실제 업무 로직을 담당한다.

---

## 18. Firestore

Firestore는 최소 다음 컬렉션을 사용한다.

* data
* conversations

서비스 계정 키를 코드에 하드코딩하지 않는다.

로컬과 Render 배포 환경에서 안전하게 환경변수로 관리할 수 있는 구조를 우선한다.

---

## 19. 필수 API

데이터:

* POST /api/data
* GET /api/data
* PUT /api/data/{id}
* DELETE /api/data/{id}
* GET /api/data/summary

대화:

* POST /api/conversations
* GET /api/conversations
* GET /api/conversations/{id}
* DELETE /api/conversations/{id}

AI:

* POST /api/chat

/api/chat 기본 흐름:

데이터 요약
→ 시스템 프롬프트에 컨텍스트 주입
→ AI API 호출
→ 대화 Firestore 저장

---

## 20. 프론트엔드

HTML/CSS/JavaScript만 사용한다.

프레임워크를 사용하지 않는다.

최소 다음 기능을 제공한다.

* AI 채팅
* 로딩 표시
* 데이터 추가 및 목록
* 수정 또는 삭제 기능
* 이전 대화 목록
* 대화 불러오기
* 데이터 요약 정보

---

## 21. 배포

Backend는 Render에 배포한다.

Frontend는 Vercel에 배포한다.

로컬 설정과 배포 설정을 분리한다.

API 키는 Render/Vercel 환경변수로 관리한다.

배포 후 Swagger /docs와 실제 프론트엔드 동작을 검증한다.

---

## 22. 코드 작성 규칙

Python 들여쓰기는 공백 4칸을 사용한다.

탭을 사용하지 않는다.

사용자에게 코드 수정을 안내할 때 가능하면 파일 전체를 제공한다.

파일이 매우 길어지는 경우에는 함수 단위 수정이 가능하지만 앞뒤 문맥을 명확히 보여준다.

Python 파일을 수정한 후 가능하면 py_compile 또는 실제 import/실행 테스트를 한다.

---

## 23. 오류 대응

사용자가 오류 로그를 제공하면 다음 순서로 설명한다.

1. 원인
2. 지금 해결할 방법
3. 다시 발생하지 않게 하는 원칙

확실하지 않으면 확실하지 않다고 말한다.

추측으로 명령을 여러 개 실행하게 하지 않는다.

필요하면 먼저 확인 명령 하나를 사용한다.

긴 로그가 필요하지 않다면 ERROR 또는 Traceback 주변과 마지막 15~30줄만 요청한다.

---

## 24. 현재 작업 상태

마지막 갱신: 2026-09-18. 이 절은 실제로 확인된 저장소 상태만 적는다.
모델의 이전 완료 주장이 아니라 커밋·diff·실행 결과를 기준으로 삼는다.

### 브랜치

* `main`이 통합 기준 브랜치다. `feat/frontend`(구현이 가장 앞선 브랜치)를
  기준으로 2026-09-18에 새로 만들고, `feat/firebase`의 VerseMate 화면과
  테스트를 그 위로 옮겨 합쳤다.
* GitHub Default Branch를 `main`으로 변경했다. (변경 직후 원격에서
  `feat/setup`으로 확인된 적이 있다. 새 세션은 `git ls-remote --symref
  origin HEAD`로 실제 반영 여부를 먼저 확인한다.)
* 과거에 갈라진 중복 브랜치 8개(`feat/setup`, `feat/api`, `feat/data`,
  `feat/conversations`, `feat/chat`, `feat/firestore-api`, `feat/ai-chat`,
  `feat/frontend`)가 아직 원격에 남아 있다. 삭제를 시도했으나 이 작업
  환경의 GitHub 자격증명에 브랜치 삭제 권한이 없어(push 403) 실패했다.
  **GitHub 웹에서 사용자가 직접 삭제해야 한다.** 이 중 `feat/data`,
  `feat/conversations`, `feat/chat`은 main에 없는 별도 커밋 이력이다
  (기능은 main에 이미 더 완전한 형태로 있음). 나머지 5개는 main의
  조상이라 삭제해도 정보 손실이 없다.
* `feat/firebase`는 의도적으로 보존한다. VerseMate 화면의 원본 커밋
  이력이며, main에는 내용만 재작성돼 들어갔다(커밋 이력 자체는 다름).

### 백엔드 (FastAPI)

* `backend/main.py`, `config.py`, `firebase_client.py`, `models.py` 구성
  완료.
* `routers/data.py`, `routers/conversations.py`, `routers/chat.py`,
  `services/summary.py`, `services/openai_client.py` 구현 완료.
* API 8개 경로가 OpenAPI에 등록됨: `/api/data`(CRUD), `/api/data/summary`,
  `/api/conversations`(CRUD), `/api/chat`.
* 테스트 53개, 전부 통과 확인(`python -m unittest discover -s tests -t .`).
  Firestore·AI는 가짜 클라이언트로 대체해 실제 외부 연결 없이 검증한다.
* Firestore 실연결, AI 모델 목록 조회 및 실제 `/api/chat` 호출은
  **아직 검증 전**이다.

### 프론트엔드

* `frontend/index.html` + `app.js` + `styles.css`/`library.css`/
  `routine.css` = VerseMate 사용자 화면(검색, TTS, QUIZ, 말씀 루틴,
  기록). 사이드바에 "데이터 관리" 링크로 admin 화면과 연결.
* `frontend/admin.html` + `admin.js` + `style.css` = 기존 API 연동
  관리 화면(데이터/대화 CRUD, 요약, 채팅). 이름만 바뀌었고 기능은
  그대로다.
* 두 화면 모두 Chromium으로 정적 로드·화면 전환까지만 확인했고,
  실제 백엔드에 붙여 전체 흐름을 검증하지는 않았다.

### 데이터

* `scripts/verses.txt`는 아직 개발용 5개 구절이다.
* `scripts/make_schedule.py`의 100개 경고 기준은 날짜 문서(시계열
  데이터 포인트) 개수로 수정 완료(2026-09-18). 구절 개수가 아니다.
  현재 계산상 구절 70개면 날짜 문서 100개를 넘는다. `seed_firestore.py`
  는 이 수정 전부터 이미 날짜 문서 기준으로 검증하고 있었다.

### 배포

* Render/Vercel 배포 설정 파일이 아직 없다(`render.yaml`,
  `vercel.json` 등 저장소에 없음).

### 개발환경

* 로컬(Windows): Python 3.13.15, PowerShell 7.6.6, Windows Terminal,
  Oh My Posh, `.venv` 사용.
* 원격(Claude Code on the web): `.claude/hooks/session-start.sh`가
  세션 시작 시 `.venv`를 만들고 `backend/requirements.txt`를 설치한다.
  로컬 PowerShell 워크플로에는 영향을 주지 않는다.

---

## 25. Codex가 세션 시작 시 먼저 할 것

코딩을 시작하기 전에 현재 상태를 추측하지 않는다.

먼저 다음을 확인한다.

* 현재 브랜치
* git status
* 프로젝트 파일 구조
* Python 실행환경
* 기존 변경사항

사용자가 작업하던 변경사항을 임의로 덮어쓰거나 삭제하지 않는다.

AGENTS.md의 규칙과 현재 저장소 상태가 충돌하면 저장소 상태를 확인하고 사용자에게 설명한다.

---

## 26. 작업 완료 보고

각 기능 작업이 끝나면 짧게 다음을 보고한다.

* 수정한 파일
* 구현된 기능
* 실행한 검증
* 남은 문제
* 다음 권장 작업

과제 요구사항 중 이번 작업이 어떤 항목을 충족했는지도 한 줄로 알려준다.
