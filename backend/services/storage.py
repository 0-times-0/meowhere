from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from core.config import settings


ALLOWED_IMAGE_SIGNATURES: dict[str, str] = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


def _detect_extension(data: bytes, content_type: str | None) -> str:
    if data.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ".webp"

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=(
            f"Nieobsługiwany format obrazu ({content_type or 'nieznany'}). "
            "Dozwolone są pliki JPG, PNG oraz WEBP."
        ),
    )


async def save_uploaded_image(file: UploadFile) -> str:
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    data = await file.read(max_bytes + 1)

    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Przesłany plik jest pusty.",
        )

    if len(data) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Plik przekracza limit {settings.MAX_UPLOAD_SIZE_MB} MB.",
        )

    ext = _detect_extension(data, file.content_type)
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid4().hex}{ext}"
    destination = upload_dir / filename
    destination.write_bytes(data)

    return f"/uploads/{filename}"