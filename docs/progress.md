# 영어성경 암송 AI 비서 — 진행상황

## 1. 현재 환경

- OS: Windows 11
- Terminal: Windows Terminal
- PowerShell: 7.6.6
- Python: 3.13.15
- Git: 설치 및 사용 중
- GitHub CLI: 설치 및 로그인 완료
- 현재 로컬 작업 브랜치: feat/api
- GitHub 저장소: kwork0828/bible-memo-assistant
- 저장소 공개 여부: Public

---

## 2. 완료된 작업

### 환경 및 Git

- 프로젝트 폴더 생성
- Git 저장소 초기화
- feat/setup 브랜치 생성
- feat/api 브랜치 생성
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
- Python 3.13.15에서 필수 패키지 import 성공
- `backend/requirements.txt` 생성
- `backend/.env.example` 생성

### 영어성경 암송 일정 생성

- `scripts/verses.txt` 생성
- World English Bible(WEB) 개발 테스트 구절 5개 준비
- `scripts/make_schedule.py` 생성
- 복습 간격 구현
  - D+0
  - D+1
  - D+3
  - D+7
  - D+14
  - D+30
- 날짜별 `date`, `value`, `memo` 데이터 생성
- 신규 학습과 복습 데이터 분리
- 100개 미만 데이터 경고 구현
- Python 3.13.15에서 문법 검사 및 실행 성공
- 개발 테스트용 일정 JSON 정상 생성

### FastAPI 기본 서버

- `backend/main.py` 생성
- FastAPI 애플리케이션 생성
- `GET /` 구현
- `GET /health` 구현
- CORSMiddleware 적용
- Swagger `/docs` 정상 동작 확인
- `/openapi.json` 정상 응답 확인
- 로컬 Uvicorn 실행 성공
- 브라우저에서 `/`, `/health`, `/docs` 모두 정상 확인

---

## 3. 주요 커밋

- `8a57606` chore: initialize project environment
- `7b7349f` docs: add project progress notes
- `a9dc3b9` docs: update project progress for codex handoff
- `180215f` feat: add memorization schedule generator
- `5195fea` feat: add FastAPI application skeleton

---

## 4. 보안 상태

다음 항목은 GitHub에 올리지 않는다.

- `.env`
- `.venv`
- `backend/firebase-service-account.json`
- 실제 OpenAI API 키
- 실제 교육기관 API 키

커밋 전에는 반드시 다음 순서로 확인한다.

1. 편집기에서 Ctrl+S 저장
2. 실행 중 프로그램 또는 서버 Ctrl+C 종료
3. `git status` 확인
4. `.env`, `.venv`, Firebase 키가 목록에 없는지 확인
5. `git add .`
6. `git commit -m "..."`
7. `git push`

---

## 5. AI API 방향

- OpenAI-compatible 구조로 설계
- 특정 AI 제공자에 코드가 종속되지 않도록 구성
- 교육기관 제공 API는 사용 가능 여부 확인 후 테스트 용도로 활용
- 교육 종료, 정책 변경, 사용자 증가, 토큰 한도 문제 발생 시 개인 OpenAI API로 쉽게 교체 가능하도록 설계
- API 키는 환경변수로만 관리
- 모델명을 추측하지 않음
- 실제 `/v1/models` 조회 후 존재하는 모델만 사용
- AI 호출 시 출력 토큰 제한 적용
- API 호출 실패 시 예외 처리 및 로그 기록

---

## 6. 데이터 전략

- 개발 단계에서는 소수 구절로 파이프라인 먼저 검증
- 현재 5개 WEB 구절로 일정 생성 기능 검증 완료
- 최종 제출 전 최소 100개 이상의 시계열 데이터 포인트 확보
- `make_schedule.py`에서 100개 미만이면 경고 출력
- 최종 제출 전 데이터 개수를 실제 실행 결과로 다시 확인

---

## 7. 현재 브랜치 상태

- 이전 작업 브랜치: `feat/setup`
- 현재 작업 브랜치: `feat/api`
- `feat/api`는 일정 생성 완료 커밋에서 분기
- FastAPI 기본 서버 커밋 `5195fea`가 `origin/feat/api`에 push 완료

---

## 8. 다음 작업

1. Firebase 프로젝트 및 Firestore 준비
2. `backend/firebase_client.py` 설계
3. Firebase 서비스 계정 키를 안전하게 환경변수로 연결
4. Firestore `data` 컬렉션 연결 검증
5. 데이터 API 구현
   - POST /api/data
   - GET /api/data
   - PUT /api/data/{id}
   - DELETE /api/data/{id}
   - GET /api/data/summary
6. 대화 API 구현
7. AI 채팅 및 데이터 요약 컨텍스트 연결
8. Render 배포
9. HTML/CSS/JavaScript 프론트엔드 구현
10. Vercel 배포
11. README 및 제출 캡처 정리

---

## 9. Codex 인수인계

Codex에서 이어서 작업할 때는 다음 순서로 진행한다.

1. `AGENTS.md` 전체 확인
2. `docs/progress.md` 전체 확인
3. 현재 브랜치 및 최신 커밋 확인
4. 현재 저장소 구조 확인
5. 다음 기능 하나만 작업
6. 테스트 결과와 수정 파일을 보고
7. GitHub push는 사용자의 로컬 환경에서 최종 확인 후 수행

현재 다음 개발 단계는 Firebase Firestore 연결 준비이다.