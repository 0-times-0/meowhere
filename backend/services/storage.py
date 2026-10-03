import shutil
import uuid
from pathlib import Path
from typing import Optional
from fastapi import UploadFile

# Folder 'uploads' na poziomie backendu: backend/uploads
UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = "http://127.0.0.1:8000/media"

async def upload_image_to_storage(file: UploadFile) -> str:
    """
    Zapisuje plik lokalnie i zwraca czysty URL gotowy do zapisu w bazie danych.
    """
    extension = Path(file.filename).suffix if file.filename else ".jpg"
    unique_filename = f"{uuid.uuid4()}{extension}"
    destination_path = UPLOAD_DIR / unique_filename

    with destination_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return f"{BASE_URL}/{unique_filename}"

def url_to_local_path(url: Optional[str]) -> Optional[Path]:
    """
    Konwertuje http://127.0.0.1:8000/media/<nazwa>.jpg na ścieżkę Path na dysku.
    """
    if not url or not url.startswith(BASE_URL):
        return None
    filename = url.replace(f"{BASE_URL}/", "")
    file_path = UPLOAD_DIR / filename
    return file_path if file_path.exists() else None
