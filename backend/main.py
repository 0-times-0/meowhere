from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.auth import router as auth_router
from api.reports import router as reports_router
from api.uploads import router as uploads_router
from core.config import settings
from core.database import init_db


# Tworzy tabele i włącza PostGIS (definicja w core/database.py).
init_db()

upload_dir = Path(settings.UPLOAD_DIR)
upload_dir.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="MEOWHERE API",
    description="System geolokalizacji zaginionych i odnalezionych zwierząt.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routery wyłącznie pod /api — frontend korzysta z tych ścieżek,
# a aliasy bez /api generowały duplikaty tras i mylące ostrzeżenia w OpenAPI.
app.include_router(auth_router, prefix="/api")
app.include_router(reports_router, prefix="/api")
app.include_router(uploads_router, prefix="/api")

# Statyczne zdjęcia: /uploads/<plik>. Montujemy PO routerach,
# żeby mount nie przesłaniał tras API.
app.mount("/uploads", StaticFiles(directory=str(upload_dir)), name="uploads")


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}