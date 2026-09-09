# 영어성경 암송 AI 비서 — 진행상황

## 1. 현재 환경

- OS: Windows 11
- Terminal: Windows Terminal
- PowerShell: 7.6.6
- Python: 3.13.15
- Git: 설치 및 사용 중
- GitHub CLI: 설치 및 로그인 완료
- 현재 브랜치: feat/setup
- GitHub 저장소: kwork0828/bible-memo-assistant
- 저장소 공개 여부: Public

---

## 2. 완료된 작업

- 프로젝트 폴더 생성
- Git 저장소 초기화
- main 브랜치 생성
- feat/setup 브랜치 생성
- Python 가상환경 `.venv` 생성
- `.gitignore` 작성
- `AGENTS.md` 작성
- `docs/progress.md` 작성
- 필수 Python 패키지 설치
  - fastapi
  - uvicorn
  - firebase-admin
  - openai
  - python-dotenv
- Python 3.13.15에서 필수 패키지 import 성공
- `backend/requirements.txt` 생성
- `backend/.env.example` 생성
- 첫 Git 커밋 완료
- GitHub Public 저장소 생성 완료
- 로컬 저장소와 `origin` 연결 완료
- `feat/setup` 브랜치 GitHub push 완료
- API 키 및 `.venv` Git 제외 확인

---

## 3. 보안 상태

다음 항목은 GitHub에 올리지 않는다.

- `.env`
- `.venv`
- `backend/firebase-service-account.json`
- 실제 OpenAI API 키
- 실제 교육기관 API 키

커밋 전에는 반드시 다음 순서로 확인한다.

1. 메모장 Ctrl+S 저장
2. 실행 중 프로그램 Ctrl+C 종료
3. `git status` 확인
4. `.env`, `.venv`, Firebase 키가 목록에 없는지 확인
5. `git add .`
6. `git commit -m "..."`
7. `git push`

---

## 4. AI API 방향

- OpenAI-compatible 구조로 설계
- 특정 API 제공자에 코드가 종속되지 않도록 구성
- 교육기관 제공 OpenAI 호환 API는 테스트 용도로 활용 가능 여부 확인 예정
- 교육 종료, 정책 변경, 사용자 증가, 토큰 한도 문제 발생 시 개인 OpenAI API로 쉽게 교체 가능하도록 설계
- API 키는 환경변수로만 관리
- 모델명을 추측하지 않음
- 실제 `/v1/models` 조회 후 응답한 모델명을 사용
- AI 호출 시 출력 토큰 제한 적용
- API 호출 실패 시 예외 처리 및 로그 기록

---

## 5. 데이터 전략

- 현재 소수의 영어성경 구절로 파이프라인 먼저 검증
- 최종 제출 전 최소 100개 이상의 시계열 데이터 포인트 확보
- `make_schedule.py`에서 구절 수가 100개 미만이면 경고 출력
- 개발 테스트는 5개 구절로 가능
- 최종 제출 시 100개 이상 데이터로 재생성

### 복습 간격

- D+0: 신규 학습
- D+1: 1차 복습
- D+3: 2차 복습
- D+7: 3차 복습
- D+14: 4차 복습
- D+30: 5차 복습

---

## 6. 다음 작업

1. Codex에서 GitHub 저장소 연결
2. Codex가 `AGENTS.md`와 `docs/progress.md`를 읽었는지 확인
3. 현재 저장소 상태 확인
4. `scripts/verses.txt` 준비 상태 확인
5. `make_schedule.py` 작성
6. 5개 구절로 테스트 데이터 생성
7. 100개 이상 데이터로 확장