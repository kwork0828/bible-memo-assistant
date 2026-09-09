영어성경 암송 AI 비서 — 진행상황
현재 환경
OS: Windows 11
Terminal: Windows Terminal
PowerShell: 7.x
Python: 3.13.15
Git 사용 중
현재 브랜치: feat/setup
완료된 작업
프로젝트 폴더 생성
Git 저장소 초기화
main 브랜치 생성
feat/setup 브랜치 생성
Python 가상환경 .venv 생성
.gitignore 작성
AGENTS.md 작성
필수 Python 패키지 설치
fastapi
uvicorn
firebase-admin
openai
python-dotenv
Python 3.13.15에서 필수 패키지 import 성공
backend/requirements.txt 생성
backend/.env.example 생성
첫 Git 커밋 완료
API 키 및 .venv Git 제외 확인
AI API 방향
OpenAI-compatible 구조로 설계
특정 API 제공자에 코드가 종속되지 않도록 구성
교육기관 제공 API를 테스트 용도로 활용 가능 여부 확인 예정
교육 종료, 정책 변경, 사용자 증가 등의 상황에서는 개인 OpenAI API로 쉽게 교체 가능하도록 설계
API 키는 환경변수로만 관리
모델명은 추측하지 않고 실제 /v1/models 조회 후 결정
AI 호출 시 출력 토큰 제한 적용
데이터 전략
현재 소수의 영어성경 구절로 파이프라인 먼저 검증
최종 제출 전 100개 이상의 데이터 포인트 확보
make_schedule.py에서 100개 미만이면 경고 출력
복습 간격:
D+0
D+1
D+3
D+7
D+14
D+30
다음 작업
GitHub Public 저장소 생성 및 push
Codex에서 저장소 연결 후 AGENTS.md 읽기
현재 저장소 상태 확인
scripts/verses.txt 상태 확인
make_schedule.py 설계 및 5개 데이터 테스트
100개 이상 데이터 확장
주의
.env를 GitHub에 올리지 않는다.
.venv를 GitHub에 올리지 않는다.
Firebase 서비스 계정 키를 GitHub에 올리지 않는다.
실제 API 키를 문서나 대화에 붙여넣지 않는다.
커밋 전 반드시 git status로 비밀파일 포함 여부를 확인한다.