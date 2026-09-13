import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv


DEFAULT_ALLOWED_ORIGINS = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
]

# 로컬에서는 backend/.env를 읽고, Render에서는 기존 환경변수를 유지한다.
load_dotenv(dotenv_path=Path(__file__).with_name(".env"), override=False)


def get_allowed_origins() -> list[str]:
    """ALLOWED_ORIGINS를 읽어 CORS 허용 주소 목록으로 반환한다."""
    raw_origins = os.getenv("ALLOWED_ORIGINS", "")
    allowed_origins = [
        origin.strip()
        for origin in raw_origins.split(",")
        if origin.strip()
    ]
    return allowed_origins or DEFAULT_ALLOWED_ORIGINS.copy()


allowed_origins = get_allowed_origins()


app = FastAPI(
    title="Bible Memo Assistant API",
    version="0.1.0",
    description="영어성경 암송 AI 비서 백엔드 API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {
        "message": "Bible Memo Assistant API is running.",
        "status": "ok",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }
