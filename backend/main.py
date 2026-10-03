from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.database import init_db
from api.reports import router as reports_router

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")

# Obsługa CORS dla frontendu Vite/React (port domyślny 5173 lub 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(reports_router)

@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.PROJECT_NAME}