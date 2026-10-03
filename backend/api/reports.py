from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session

from core.database import get_db
from models.report import Report
from schemas.report import ReportCreate, ReportResponse
from services.spatial import create_report, get_reports_filtered
from services.storage import upload_image_to_storage
from services.ai_matcher import process_found_pet_ai_matching

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/upload-image", summary="Upload zdjęcia do lokalnej chmury")
async def upload_image(file: UploadFile = File(...)):
    """
    Odbiera plik graficzny z formularza, zapisuje go i zwraca czysty URL dla frontendu.
    """
    photo_url = await upload_image_to_storage(file)
    return {"photo_url": photo_url}


@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def add_report(
    report_data: ReportCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Tworzy nowe zgłoszenie w PostGIS.
    Jeśli wpis dodaje Straż Miejska (status = found_patrol) ze zdjęciem,
    w tle uruchamia się model AI szukający dopasowań.
    """
    new_report = create_report(db=db, report_data=report_data)

    # Logika AI w tle dla patrolu Straży Miejskiej
    if new_report.status == "found_patrol" and new_report.photo_url:
        background_tasks.add_task(
            process_found_pet_ai_matching,
            new_report.id,
            new_report.photo_url
        )

    return new_report

# (Pozostałe endpointy get_reports i get_report_by_id zostają bez zmian)
