# 배포 가이드 (Render + Vercel)

이 문서는 `render.yaml`과 `vercel.json`이 무엇을 설정해두는지, 그리고
그 다음으로 **사용자가 직접** 각 서비스 웹사이트에서 해야 하는 일을
정리한다. 계정 로그인과 GitHub 저장소 연결은 AI가 대신할 수 없는
작업이다.

## 준비물

* Render 계정 (GitHub으로 가입 가능)
* Vercel 계정 (GitHub으로 가입 가능)
* Firebase 서비스 계정 JSON (로컬에서 이미 쓰고 있는 것)
* 실제 OpenAI 또는 OpenAI-compatible API 키

키 값은 이 문서에도, 커밋에도, 채팅에도 적지 않는다. 전부 Render/Vercel
웹 대시보드에 직접 입력한다.

---

## 1단계: 백엔드를 Render에 배포

1. https://dashboard.render.com 접속 → **New +** → **Blueprint**
2. `kwork0828/bible-memo-assistant` 저장소 선택, 브랜치는 `main`
3. Render가 저장소 루트의 `render.yaml`을 읽어 서비스 하나
   (`bible-memo-assistant-api`)를 자동으로 구성한다.
4. 배포 전에 **Environment** 탭에서 다음 값을 직접 입력한다
   (`render.yaml`에는 값이 없고 키 이름만 있다 — `sync: false`로
   표시된 항목):
   * `AI_PROVIDER`
   * `OPENAI_API_KEY`
   * `OPENAI_BASE_URL`
   * `OPENAI_MODEL` — §14 절차(모델 목록 실제 조회 후 입력)를 먼저 거친다
   * `FIREBASE_SERVICE_ACCOUNT_JSON` — 서비스 계정 JSON 전체를 한 줄로
     붙여넣는다
   * `ALLOWED_ORIGINS` — 2단계에서 Vercel 주소가 나오기 전까지는
     `http://localhost:5500` 같은 임시값을 넣어둬도 된다
5. 배포가 끝나면 Render가 `https://bible-memo-assistant-api-xxxx.onrender.com`
   같은 주소를 준다.
6. 검증:
   * `<그 주소>/health` → `{"status":"healthy"}`
   * `<그 주소>/docs` → Swagger UI가 열리는지, `/api/data`,
     `/api/conversations`, `/api/chat`이 목록에 보이는지 확인

## 2단계: 프론트엔드를 Vercel에 배포

1. https://vercel.com/new 접속 → 같은 저장소 Import
2. `vercel.json`이 저장소 루트에 있으므로 Framework Preset은
   자동으로 "Other", 빌드 명령 없이 `frontend/` 폴더를 그대로
   정적 사이트로 서비스한다. 별도 설정을 바꿀 필요는 없다.
3. Deploy 클릭 → `https://<프로젝트명>.vercel.app` 같은 주소를 받는다.
4. 브라우저에서 그 주소를 열고, 왼쪽 사이드바의 "데이터 관리"를 눌러
   `admin.html`로 이동한 뒤 화면 위쪽 "Backend API 주소" 입력칸에
   1단계에서 받은 Render 주소를 입력한다.

## 3단계: 백엔드 CORS를 실제 프론트엔드 주소로 좁히기

1. Render 대시보드 → `bible-memo-assistant-api` → Environment
2. `ALLOWED_ORIGINS` 값을 2단계에서 받은 Vercel 주소로 바꾼다.
   예: `https://bible-memo-assistant.vercel.app`
3. 저장하면 Render가 자동으로 재시작한다.

## 4단계: 전체 흐름 확인

1. Vercel 주소 → `index.html`(VerseMate 사용자 화면)이 정상 표시되는지
2. `admin.html`에서 데이터 추가/조회 → Render API → Firestore까지
   실제로 저장되는지
3. AI 코치(채팅)에서 실제 응답이 오는지, 실패 시 502로 처리되는지
4. Render `/docs`에서 Swagger로 각 API를 한 번씩 직접 호출해보기

---

## 로컬에서 미리 검증하고 싶다면

배포 전에 본인 PC에서 먼저 확인하고 싶다면 아래 순서를 쓴다
(전부 이미 만들어져 있는 스크립트다):

```
scripts/setup_local_firebase_env.py   # backend/.env 안전하게 준비
scripts/check_firebase.py             # Firestore 연결 확인
scripts/list_ai_models.py             # 실제 사용 가능한 모델 목록 조회
scripts/check_api_routes.py           # FastAPI 라우트 등록 확인
```

이 스크립트들은 키 값을 화면에 출력하지 않도록 이미 작성돼 있다.
