from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import ALLOWED_ORIGINS
from backend.routers.chat import router as chat_router
from backend.routers.conversations import router as conversations_router
from backend.routers.data import router as data_router


app = FastAPI(
    title="Bible Memo Assistant API",
    version="0.1.0",
    description="영어성경 암송 AI 비서 백엔드 API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(data_router)
app.include_router(conversations_router)
app.include_router(chat_router)


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
