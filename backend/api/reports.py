from typing import Any, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Response,
    status,
)
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import Principal, get_current_principal
from models.report import Report
from schemas.report import (
    ReportCreate,
    ReportResponse,
    ReportStatus,
    ReportSummaryResponse,
    Species,
)
from services.ai_matcher import find_matches_for_report
from services.spatial import (
    SpatialFilterError,
    create_report,
    get_reports_filtered,
    get_reports_for_principal,
)


router = APIRouter(prefix="/reports", tags=["reports"])


@router.post(
    "/",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_report(
    report_data: ReportCreate,
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
) -> Report:
    return create_report(
        db=db,
        report_data=report_data,
        principal=principal,
    )


@router.get(
    "/",
    response_model=list[ReportSummaryResponse],
)
def get_reports(
    lat: Optional[float] = Query(None, ge=-90, le=90),
    lon: Optional[float] = Query(None, ge=-180, le=180),
    radius_km: Optional[float] = Query(None, ge=0.1, le=100),
    min_lat: Optional[float] = Query(None, ge=-90, le=90),
    min_lon: Optional[float] = Query(None, ge=-180, le=180),
    max_lat: Optional[float] = Query(None, ge=-90, le=90),
    max_lon: Optional[float] = Query(None, ge=-180, le=180),
    species: Optional[Species] = Query(None),
    report_status: Optional[ReportStatus] = Query(None, alias="status"),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[Report]:
    try:
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
            status=report_status,
            limit=limit,
        )
    except SpatialFilterError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.get(
    "/mine",
    response_model=list[ReportResponse],
)
def get_my_reports(
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
) -> list[Report]:
    return get_reports_for_principal(
        db=db,
        principal=principal,
    )


@router.get(
    "/{report_id}/matches",
    response_model=list[dict[str, Any]],
)
def get_report_matches(
    report_id: int,
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    report = db.query(Report).filter(Report.id == report_id).first()
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nie znaleziono zgłoszenia.",
        )
    return find_matches_for_report(db=db, report=report)


@router.get(
    "/{report_id}",
    response_model=ReportResponse,
)
def get_report_by_id(
    report_id: int,
    db: Session = Depends(get_db),
) -> Report:
    report = db.query(Report).filter(Report.id == report_id).first()
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nie znaleziono zgłoszenia.",
        )
    return report


@router.patch(
    "/{report_id}/resolve",
    response_model=ReportResponse,
)
def resolve_report(
    report_id: int,
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
) -> Report:
    report = db.query(Report).filter(Report.id == report_id).first()
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nie znaleziono zgłoszenia.",
        )

    is_owner = principal.role == "resident" and report.user_id == principal.id
    if principal.role != "municipal" and not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nie masz uprawnień do zamknięcia tego zgłoszenia.",
        )

    report.status = ReportStatus.RESOLVED.value
    try:
        db.commit()
        db.refresh(report)
    except Exception:
        db.rollback()
        raise

    return report


@router.delete(
    "/{report_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_report(
    report_id: int,
    db: Session = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
) -> Response:
    report = db.query(Report).filter(Report.id == report_id).first()
    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nie znaleziono zgłoszenia.",
        )

    is_owner = (
        principal.role == "resident" and report.user_id == principal.id
    ) or (
        principal.role == "municipal"
        and report.municipal_user_id == principal.id
    )

    if not is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nie masz uprawnień do usunięcia tego zgłoszenia.",
        )

    try:
        db.delete(report)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return Response(status_code=status.HTTP_204_NO_CONTENT)