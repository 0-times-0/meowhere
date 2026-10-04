from fastapi import APIRouter, Depends, File, UploadFile, status
from pydantic import BaseModel

from core.security import Principal, get_current_principal
from services.storage import save_uploaded_image


router = APIRouter(prefix="/uploads", tags=["uploads"])


class UploadResponse(BaseModel):
    photo_url: str


@router.post(
    "/",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_report_photo(
    file: UploadFile = File(...),
    _principal: Principal = Depends(get_current_principal),
) -> UploadResponse:
    """Przyjmuje plik obrazu od zalogowanego użytkownika i zwraca URL."""
    photo_url = await save_uploaded_image(file)
    return UploadResponse(photo_url=photo_url)