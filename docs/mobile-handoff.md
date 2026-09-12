# 모바일 작업 인수인계 체크포인트

작성 목적: 사용자가 모바일 상태일 때도 GitHub 기준으로 어디까지 구현됐는지 확인하고, 다음 개인 PC 세션에서 바로 검증을 시작하기 위한 문서.

## 최신 통합 브랜치

`feat/frontend`

이 브랜치는 다음 작업을 모두 포함한다.

- `feat/setup`
- `feat/api`
- `feat/firebase`
- `feat/firestore-api`
- `feat/ai-chat`
- `feat/frontend`

## 이번 모바일 세션에서 추가 구현한 것

### Backend

- Firestore `data` CRUD API
- `data` summary API
- `conversations` 저장/목록/단건조회/삭제 API
- OpenAI-compatible AI client
- 실제 모델 목록 조회 스크립트
- `/api/chat` 데이터 요약 주입 + AI 응답 + 대화 저장 흐름
- AI JSON 응답 파싱
- 코드 펜스 제거
- thought/reasoning 계열 필드 제거
- 출력 토큰 제한 / 제한된 재시도 / 로그
- Provider 오류 세부정보를 사용자 HTTP 응답에 그대로 노출하지 않도록 처리

### Frontend

- Vanilla HTML/CSS/JavaScript 화면
- data 요약
- data 추가/수정/삭제/목록
- 삭제 확인창
- AI 채팅
- 로딩 상태
- 이전 대화 목록/불러오기/삭제
- Backend API 주소 저장
- 모바일 반응형 레이아웃

### 검증·운영 도구

- `scripts/setup_local_firebase_env.py`
- `scripts/check_firebase.py`
- `scripts/check_api_routes.py`
- `scripts/list_ai_models.py`
- `scripts/seed_firestore.py`
  - 기본은 dry-run
  - 100개 미만 데이터는 기본 차단
  - 개발 테스트는 `--allow-small`을 명시해야 허용
  - 실제 쓰기는 `--write`를 추가해야 실행
  - 같은 날짜가 이미 있으면 건너뜀
- `tests/test_core.py`
  - 날짜/음수 값 검증
  - 외부 system role 차단
  - summary 계산
  - Firebase 설정 파싱
  - AI JSON/코드펜스/thought 필터 검증

### 문서

- `README.md`
- `docs/architecture.md`
- `docs/review-guide.md`
- `docs/progress.md`

## 현재 판정

### 코드 구현량

약 70% 수준.

### 실제 완료도

약 55~60% 수준.

코드가 존재하는 것과 실제 운영 성공을 구분한다.

## 아직 Major인 항목

1. 실제 서비스 계정으로 `FIREBASE_CONNECTION_OK` 확인 필요
2. 실제 Firestore data/conversations CRUD 통합 테스트 필요
3. 실제 AI Provider `/v1/models` 조회 필요
4. 실제 존재 모델로 `/api/chat` 호출 필요
5. Frontend ↔ FastAPI ↔ Firestore ↔ AI 전체 흐름 검증 필요

## 아직 하지 않은 외부 변경

사용자 승인 없이 다음은 실행하지 않는다.

- Render 공개 배포
- Vercel 공개 배포
- `main` 병합
- 운영 데이터 삭제
- 유료 결제 또는 요금제 변경

## 개인 PC에서 다음에 할 최소 작업

1. `feat/frontend` 최신화
2. 가상환경 활성화
3. `python scripts/setup_local_firebase_env.py`
4. `python scripts/check_firebase.py`
5. `python -m unittest discover -s tests -v`
6. `python scripts/check_api_routes.py`
7. Uvicorn 실행 후 Swagger CRUD 검증
8. AI Provider가 확정되면 `python scripts/list_ai_models.py`
9. 실제 출력된 모델만 `OPENAI_MODEL`에 설정
10. `/api/chat` 한 건 테스트
11. Frontend 전체 흐름 확인

## AX 코치 관점의 승인 기준

- 파일이 있다 → 구현됨
- 테스트가 통과한다 → 로직 검증됨
- Firestore에 실제 저장된다 → 데이터 통합 검증됨
- 실제 AI 응답이 저장된다 → AI 흐름 검증됨
- 다른 기기에서 공개 URL이 열린다 → 배포 검증됨

각 단계는 앞 단계의 증거를 다음 단계의 근거로 사용하며, 모델의 “완료했습니다”라는 문장만으로 완료 판정하지 않는다.
