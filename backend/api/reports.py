from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from models.report import Report
from schemas.report import ReportCreate, ReportResponse
from services.spatial import create_report, get_reports_filtered

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def add_report(report_data: ReportCreate, db: Session = Depends(get_db)):
    """
    Tworzy nowe zgłoszenie ze współrzędnymi GPS w bazie danych PostGIS.
    """
    return create_report(db=db, report_data=report_data)


@router.get("/", response_model=List[ReportResponse])
def get_reports(
    lat: Optional[float] = Query(None, description="Szerokość geograficzna użytkownika (GPS)"),
    lon: Optional[float] = Query(None, description="Długość geograficzna użytkownika (GPS)"),
    radius_km: Optional[float] = Query(None, ge=0.1, le=100.0, description="Promień wyszukiwania w kilometrach"),
    min_lat: Optional[float] = Query(None, description="Bounding Box - minimalna szerokość"),
    min_lon: Optional[float] = Query(None, description="Bounding Box - minimalna długość"),
    max_lat: Optional[float] = Query(None, description="Bounding Box - maksymalna szerokość"),
    max_lon: Optional[float] = Query(None, description="Bounding Box - maksymalna długość"),
    species: Optional[str] = Query(None, description="Gatunek: cat, dog, other"),
    status: Optional[str] = Query(None, description="Status: lost, found_patrol, resolved"),
    limit: int = Query(100, ge=1, le=500, description="Maksymalna liczba zwracanych wpisów"),
    db: Session = Depends(get_db)
):
    """
    Zwraca listę zgłoszeń posortowaną od najnowszych.
    Umożliwia filtrowanie po promieniu (ST_DWithin), kadrze mapy (ST_MakeEnvelope) oraz gatunku i statusie.
    """
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


@router.get("/mine", response_model=List[ReportResponse])
def get_my_reports(
    user_id: Optional[int] = Query(None, description="ID użytkownika, którego zgłoszenia mają zostać pobrane"),
    municipal_user_id: Optional[int] = Query(None, description="ID pracownika straży miejskiej, którego zgłoszenia mają zostać pobrane"),
    db: Session = Depends(get_db)
):
    """
    Zwraca wszystkie zgłoszenia utworzone przez konkretnego użytkownika lub straż miejską.
    Umożliwia łatwe pobieranie i sprawdzanie własnych wpisów bez logowania.
    """
    if user_id is None and municipal_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Należy podać user_id albo municipal_user_id."
        )

    query = db.query(Report)
    if user_id is not None:
        query = query.filter(Report.user_id == user_id)
    if municipal_user_id is not None:
        query = query.filter(Report.municipal_user_id == municipal_user_id)

    return query.order_by(Report.created_at.desc()).all()


@router.get("/{report_id}", response_model=ReportResponse)
def get_report_by_id(report_id: int, db: Session = Depends(get_db)):
    """
    Pobiera pojedyncze zgłoszenie na podstawie jego ID (np. dla /listing?id={id} lub modala pinezki).
    Zwraca kod 404, jeśli dane zgłoszenie nie istnieje w bazie.
    """
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Zgłoszenie o ID {report_id} nie zostało znalezione."
        )
    return report


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report(
    report_id: int,
    user_id: Optional[int] = Query(None, description="ID właściciela zgłoszenia z tabeli users"),
    municipal_user_id: Optional[int] = Query(None, description="ID właściciela zgłoszenia z tabeli municipal_users"),
    db: Session = Depends(get_db)
):
    """
    Usuwa zgłoszenie tylko wtedy, gdy zostało utworzone przez podanego użytkownika lub straż miejską.
    """
    if user_id is None and municipal_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Należy podać user_id albo municipal_user_id."
        )

    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Zgłoszenie o ID {report_id} nie zostało znalezione."
        )

    if user_id is not None and report.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nie masz uprawnień do usunięcia tego zgłoszenia."
        )

    if municipal_user_id is not None and report.municipal_user_id != municipal_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nie masz uprawnień do usunięcia tego zgłoszenia."
        )

    db.delete(report)
    db.commit()
    return None