# Windows 검증 가이드

비개발자가 이 프로젝트를 검토할 때 아래 순서로 확인한다.

## 1. 저장소 최신화

현재 가장 많은 기능이 들어 있는 작업 브랜치는 `feat/frontend`이다.

확인 순서:

1. Git 상태 확인
2. `feat/frontend` 브랜치로 이동
3. 원격 최신 내용 받기
4. `.env`, `.venv`, Firebase 키가 Git 목록에 없는지 확인

## 2. Python 환경

가상환경을 활성화한 뒤 다음 패키지가 import 되는지 확인한다.

- fastapi
- uvicorn
- firebase_admin
- openai
- dotenv

`backend/requirements.txt`가 기준 패키지 목록이다.

## 3. Firebase 로컬 설정

실제 비밀키 파일은 다음 위치에 둔다.

`backend/firebase-service-account.json`

이 파일은 GitHub에 올리지 않는다.

그 다음:

1. `scripts/setup_local_firebase_env.py`
2. `scripts/check_firebase.py`

순서로 실행한다.

성공 기준:

- `LOCAL_FIREBASE_ENV_OK`
- `FIREBASE_CONNECTION_OK`

## 4. API 구조 확인

`scripts/check_api_routes.py`를 실행한다.

성공 기준:

`API_ROUTE_CHECK_OK`

이후 Uvicorn 서버를 실행하고 브라우저에서 `/docs`를 연다.

확인 대상:

- `/`
- `/health`
- data API 5개
- conversations API 4개
- `/api/chat`

## 5. Firestore CRUD 확인

Swagger `/docs`에서 테스트 데이터를 한 건 만들어 아래 순서로 확인한다.

1. POST `/api/data` → 생성 성공
2. GET `/api/data` → 생성 데이터 조회
3. GET `/api/data/summary` → count/value 반영
4. PUT `/api/data/{id}` → 값 수정
5. DELETE `/api/data/{id}` → 삭제
6. GET `/api/data` → 삭제 반영

삭제는 테스트 문서 ID를 다시 확인한 뒤 실행한다.

## 6. Conversation API 확인

1. POST `/api/conversations`
2. GET `/api/conversations`
3. GET `/api/conversations/{id}`
4. DELETE `/api/conversations/{id}`

`role`은 `user` 또는 `assistant`만 허용하는지 확인한다.

## 7. AI Provider 확인

모델명을 추측해서 입력하지 않는다.

먼저 Provider의 API 키와 base URL을 로컬 `.env`에 설정한 뒤 `scripts/list_ai_models.py`를 실행한다.

성공 기준:

`MODEL_LIST_OK`

실제 출력된 모델 중 하나를 `OPENAI_MODEL`에 입력한다.

그 다음 `/api/chat` 한 건만 작은 입력으로 테스트한다.

확인 항목:

- AI 응답 성공
- 응답이 화면에 표시됨
- conversations 컬렉션에 사용자/assistant 메시지가 저장됨
- thought/reasoning 필드가 사용자 응답에 노출되지 않음
- 코드 펜스가 사용자 답변에 남지 않음

## 8. Frontend 확인

`frontend/index.html`을 브라우저에서 확인한다.

기본 API 주소는 `http://127.0.0.1:8000`이다.

확인 항목:

- 데이터 요약
- data 추가
- data 수정
- data 삭제 전 확인창
- 채팅 로딩 표시
- AI 답변
- 이전 대화 목록
- 대화 불러오기
- 대화 삭제 전 확인창

## 9. 완료 판정

다음 증거를 구분한다.

- 코드 파일이 존재한다 → 구현 증거
- 문법 검사가 성공한다 → 정적 검증 증거
- 로컬 API 호출이 성공한다 → 실행 증거
- Firestore Console에 값이 실제 저장된다 → 저장 증거
- 공개 URL을 다른 브라우저/기기에서 확인한다 → 배포 증거

구현 파일이 있다는 이유만으로 운영 성공이라고 판정하지 않는다.

## 10. 현재 남은 큰 작업

- 실제 Firebase 통합 테스트
- 실제 AI 모델 조회·호출 테스트
- Frontend 통합 테스트
- Render 배포
- Vercel 배포
- 100개 이상 최종 데이터
- README / 캡처 / 제출 체크리스트
