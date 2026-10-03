from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.database import init_db
from api.reports import router as reports_router
from api.auth import router as auth_router
from services.storage import UPLOAD_DIR

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Udostępnienie katalogu ze zdjęciami
app.mount("/media", StaticFiles(directory=UPLOAD_DIR), name="media")

@app.on_event("startup")
def on_startup():
    init_db()

# 2. Rejestracja routerów
app.include_router(auth_router)
app.include_router(reports_router)

@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.PROJECT_NAME}
