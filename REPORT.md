# 영어성경 암송 AI 비서 작업 보고서

작성일: 2026-09-14  
현재 브랜치: `feat/firebase`  
저장소: [kwork0828/bible-memo-assistant](https://github.com/kwork0828/bible-memo-assistant/tree/feat/firebase)

## 1. 프로젝트 한 줄 소개

영어성경 구절을 일정에 따라 암송하고, 복습 결과와 묵상을 기록하며, 말씀을 오늘의 행동으로 연결하는 개인 학습용 AI 비서입니다.

핵심 흐름은 다음과 같습니다.

```text
영어성경 검색
    ↓
본문 읽기·듣기·암송
    ↓
말씀 실천 루틴 작성
    ↓
오늘의 행동 실행
    ↓
묵상·적용 기록 모아보기
```

## 2. 과제 요구사항 대응표

| 과제·기획 항목 | 현재 대응 | 상태 |
|---|---|---|
| FastAPI 백엔드 | `backend/main.py`와 라우터 구조 | 구현·테스트 완료 |
| Firestore 연동 구조 | lazy 초기화 클라이언트와 `data`, `conversations` 컬렉션 라우터 | 구조 구현, 화면 연결 진행 중 |
| 영어성경 암송 일정 | D+0, D+1, D+3, D+7, D+14, D+30 | 구현 완료 |
| 100개 이상 시계열 데이터 | `scripts/make_schedule.py`에 100개 미만 경고 | 현재 5개 개발 데이터 |
| 영어성경 원문 검색 | 장·절과 본문 검색, WEB 예시 구절 | 목업 구현 |
| 검색 결과 장·절 표시 | `Genesis 39:9` 등 reference 표시 | 구현 완료 |
| 본문 전체 클릭 | 검색 카드 전체를 클릭해 오늘 학습으로 선택 | 구현 완료 |
| 음성 속도 조절 | 0.75×, 1×, 1.25× | 브라우저 목업 구현 |
| 자막 | 음성 재생 중 본문 표시 | 브라우저 목업 구현 |
| QUIZ 모드 | 일부 단어를 네모 빈칸으로 표시 | 브라우저 목업 구현 |
| 묵상·감상노트 | 한 줄 평과 말씀 실천 기록 | 브라우저 임시 저장 구현 |
| 말씀을 삶에 적용 | 성찰·계획·실행·회고 단계 | 브라우저 임시 저장 구현 |
| 창세기 39장 요셉 적용 | 정직·경계선·유혹 탈출 질문과 예시 | 목업 구현 |
| AI 채팅 | 현재는 일정 기반 목업 응답 | 실제 AI API 연결 전 |
| SNS·블로그 공유 | 블로그·Threads·짧은 SNS 초안 생성 후 복사 | 목업 구현 |
| 자동 SNS 게시 | 계정 연동 및 외부 게시 | 의도적으로 미구현 |
| Render/Vercel 배포 | 배포 설정 전 | 미완료 |

## 3. 이번 작업에서 바뀐 사용자 경험

### 암송 화면

- `본문 가리기`: 영어 본문을 흐리게 표시
- `본문 보기`: 원문 복원
- `QUIZ 모드`: 일부 단어를 `????` 빈칸으로 표시
- `답 확인`: 점수와 함께 사용자가 입력한 답을 별도 검토 상자에 표시
- `답 수정하기`: 입력창으로 돌아가 다시 작성 가능
- `영어 듣기`: 브라우저 음성 기능 사용
- 속도 선택: 0.75× / 1× / 1.25×
- 자막 표시: 재생 중 영어 본문 표시

### 말씀 실천 루틴

기존 `BOD`라는 표현은 화면에서 제거하고 `말씀 루틴`으로 변경했습니다. 화면상 단계는 다음과 같습니다.

1. 성찰: 하나님과 내 마음을 돌아보기
2. 계획: 오늘 실천할 한 가지와 시간을 정하기
3. 실행: 정직 기준과 유혹 탈출 행동을 미리 정하기
4. 회고: 실행 여부와 다음 개선점 돌아보기

첫 암송 완료 직후에는 네 가지 질문을 강제로 보여주지 않습니다. 한 줄 평만 남기고, 상세 적용은 `말씀 루틴` 화면에서 작성하도록 분리했습니다.

### 요셉 적용 모드

창세기 39장의 내용을 다음 행동 기준으로 번역했습니다.

- 하나님이 함께하심을 기억하기
- 사람이 보지 않아도 맡은 일을 정직하게 하기
- 불의와 타협하지 않을 선을 미리 정하기
- 유혹과 협상하지 않고 위험한 자리에서 떠나기

## 4. 화면 이동 구조

왼쪽 탭은 숫자 대신 기능 이니셜을 사용합니다.

| 이니셜 | 화면 | 역할 |
|---|---|---|
| D | 오늘 학습 | 오늘 암송할 말씀과 진행률 |
| R | 복습 일정 | 날짜별 신규·복습 큐 |
| L | 영어성경 | 검색·즐겨찾기·파일 업로드 |
| P | 말씀 루틴 | 성찰·계획·실행·회고 |
| C | AI 코치 | 학습 질문과 코칭 |
| J | 내 기록 | 묵상·실천 기록과 꾸준함 |

## 5. 폴더 구조와 역할

```text
bible-memo-assistant/
├─ backend/
│  ├─ main.py                 # FastAPI 앱, CORS, 라우터 등록
│  ├─ config.py               # 환경변수 로드
│  ├─ firebase_client.py       # Firebase lazy 초기화
│  ├─ models.py                # Pydantic 요청·응답 모델
│  ├─ routers/
│  │  ├─ data.py              # 암송 일정 CRUD·요약·인사이트
│  │  └─ conversations.py     # 대화·묵상 CRUD
│  ├─ services/
│  │  └─ summary.py           # 기간 계산과 요약 로직
│  └─ test_*.py                # 외부 Firestore 없이 실행하는 단위 테스트
├─ frontend/
│  ├─ index.html               # HTML 화면 구조
│  ├─ app.js                   # 화면 상태·검색·음성·로컬 목업 동작
│  ├─ styles.css               # 기본 디자인·반응형
│  ├─ library.css              # 영어성경 보관함 스타일
│  └─ routine.css              # 말씀 루틴·기록 스타일
├─ scripts/
│  ├─ make_schedule.py         # 복습 일정 생성
│  └─ verses.txt               # 개발용 WEB 구절 5개
├─ docs/progress.md            # 누적 진행 기록
├─ AGENTS.md                   # 프로젝트 작업 규칙
└─ REPORT.md                  # 현재 작업 설명 문서
```

## 6. 백엔드 API

현재 OpenAPI에 등록된 API는 다음과 같습니다.

| 메서드 | 경로 | 역할 |
|---|---|---|
| GET | `/` | 서버 실행 상태 |
| GET | `/health` | 헬스 체크 |
| POST | `/api/data` | 암송 일정 생성 |
| GET | `/api/data` | 일정 목록 조회 |
| PUT | `/api/data/{id}` | 일정 수정 |
| DELETE | `/api/data/{id}` | 일정 삭제 |
| GET | `/api/data/summary` | 전체 학습 요약 |
| GET | `/api/data/insights` | 주간·월간 인사이트 |
| POST | `/api/conversations` | AI 대화·묵상 저장 |
| GET | `/api/conversations` | 대화 목록 |
| GET | `/api/conversations/{id}` | 대화 하나 조회 |
| DELETE | `/api/conversations/{id}` | 대화 삭제 |

`POST /api/chat`은 아직 구현하지 않았습니다. 실제 AI Provider 연결 전에 모델 목록 조회와 환경변수 검증을 먼저 진행해야 합니다.

## 7. 데이터 흐름

### 일정 생성 흐름

```text
scripts/verses.txt
    ↓
make_schedule.py
    ↓
date / value / memo
    ↓
POST /api/data
    ↓
Firestore data 컬렉션
```

### 현재 목업의 묵상 흐름

```text
암송 완료
    ↓
한 줄 평 입력
    ↓
localStorage 임시 저장
    ↓
내 기록 화면에서 검색·조회
```

실서비스 단계에서는 마지막 저장소를 Firestore `conversations` 컬렉션으로 교체하고, 사용자별 데이터 분리를 추가해야 합니다.

## 8. 보안·저작권 원칙

- API 키를 소스 코드에 하드코딩하지 않음
- `.env`, `.venv`, Firebase 서비스 계정 파일은 Git에서 제외
- Firebase 서비스 계정 JSON 내용은 보고서와 채팅에 출력하지 않음
- 영어성경 기본 방향은 공개 배포 가능한 World English Bible(WEB)
- SNS는 자동 게시하지 않고, 사용자가 개인정보를 확인한 뒤 초안을 복사
- 실제 운영 시 로그인·사용자별 Firestore 권한 규칙이 필요

## 9. 검증 증거

2026-09-14 기준으로 다음을 실행했습니다.

```text
node --check frontend/app.js
```

결과: 통과

```text
python -m unittest discover -s . -p "test_*.py"
```

결과: `Ran 26 tests` / `OK`

추가 확인:

- Python 백엔드 compile 검사 통과
- FastAPI OpenAPI 경로 확인
- 브라우저 콘솔 오류·경고 없음
- Git 추적 목록에 `.env`, Firebase 키, `.venv` 없음

## 10. 현재 한계와 다음 개발 순서

### 현재 한계

1. WEB 데이터가 5개인 개발 단계라 전체 성경 검색은 아직 아님
2. 프론트엔드 묵상·루틴 기록은 localStorage 임시 저장
3. AI 채팅은 목업 응답이며 실제 `/api/chat` 미구현
4. 음성은 브라우저 운영체제의 SpeechSynthesis 품질에 의존
5. 로그인·사용자별 권한·배포 환경 분리 미완료

### 권장 다음 순서

1. 목업 화면 승인
2. 묵상·말씀 루틴 모델을 Firestore 저장으로 연결
3. 프론트에서 `/api/data`, `/api/conversations` 호출
4. WEB 구절 100개 이상으로 확장하고 일정 생성 검증
5. OpenAI-compatible Provider 모델 목록 조회 후 `/api/chat` 연결
6. Render 백엔드·Vercel 프론트엔드 배포
7. 실제 기기에서 `/docs`, 검색, 암송, 기록 흐름 검증

## 11. 동료에게 1분 설명하기

> 이 프로젝트는 영어성경 암송 일정을 자동으로 만들고, 오늘 외울 구절을 보여주는 FastAPI·Firestore 기반 앱입니다. 프론트엔드는 프레임워크 없이 HTML/CSS/JavaScript로 만들었습니다. 현재는 검색, 카드 전체 클릭, 음성 속도·자막, QUIZ, 말씀 루틴, 묵상 기록, SNS 초안 목업까지 구현했고, 백엔드는 일정과 대화 CRUD API 및 테스트를 준비했습니다. 다만 묵상은 아직 브라우저 임시 저장이고 AI API·배포는 다음 단계입니다. 완료 여부는 모델의 설명이 아니라 테스트 26개, OpenAPI 경로, 실제 화면 동작으로 확인합니다.

## 12. Git 작업 기록

- 작업 브랜치: `feat/firebase`
- 이번 보고서 작성 후 현재 변경사항을 함께 커밋·푸시 예정
- `main` 직접 개발 및 병합은 실행하지 않음
