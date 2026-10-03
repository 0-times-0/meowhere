from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.report import ReportCreate, ReportResponse
from services.spatial import create_report, get_reports_filtered

router = APIRouter(prefix="/reports", tags=["reports"])

@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def add_report(report_data: ReportCreate, db: Session = Depends(get_db)):
    return create_report(db=db, report_data=report_data)

@router.get("/", response_model=List[ReportResponse])
def get_reports(
    lat: Optional[float] = Query(None, description="Szerokość geograficzna (GPS)"),
    lon: Optional[float] = Query(None, description="Długość geograficzna (GPS)"),
    radius_km: Optional[float] = Query(None, ge=0.1, le=100.0, description="Promień wyszukiwania w km"),
    min_lat: Optional[float] = Query(None, description="Bounding Box - minimalna szerokość"),
    min_lon: Optional[float] = Query(None, description="Bounding Box - minimalna długość"),
    max_lat: Optional[float] = Query(None, description="Bounding Box - maksymalna szerokość"),
    max_lon: Optional[float] = Query(None, description="Bounding Box - maksymalna długość"),
    species: Optional[str] = Query(None, description="Gatunek: cat, dog, other"),
    status: Optional[str] = Query(None, description="Status: lost, found_patrol, resolved"),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    return get_reports_filtered(
        db=db,
        lat=lat,
        lon=lon,
        radius_km=radius_km,
        min_lat=min_lat,
        min_lon=min_lon,
        max_lat=max_lat,
        max_lon=max_lon,
        species=species,
        status=status,
        limit=limit
    )