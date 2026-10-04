import math
from enum import Enum

from geoalchemy2.elements import WKTElement
from geoalchemy2.types import Geography
from sqlalchemy import cast, func
from sqlalchemy.orm import Session

from core.security import Principal
from models.report import Report
from schemas.report import ReportCreate, ReportStatus, Species


class SpatialFilterError(ValueError):
    """Niekompletny lub niepoprawny filtr przestrzenny."""


def _enum_value(value):
    if isinstance(value, Enum):
        return value.value
    return value


def _validate_spatial_filters(
    *,
    lat: float | None,
    lon: float | None,
    radius_km: float | None,
    min_lat: float | None,
    min_lon: float | None,
    max_lat: float | None,
    max_lon: float | None,
) -> None:
    center_values = (lat, lon, radius_km)
    center_filter_requested = any(value is not None for value in center_values)

    if center_filter_requested and any(value is None for value in center_values):
        raise SpatialFilterError(
            "Filtr promienia wymaga podania lat, lon i radius_km."
        )

    if lat is not None and (
        not math.isfinite(lat) or not -90 <= lat <= 90
    ):
        raise SpatialFilterError("lat musi mieścić się w zakresie od -90 do 90.")

    if lon is not None and (
        not math.isfinite(lon) or not -180 <= lon <= 180
    ):
        raise SpatialFilterError("lon musi mieścić się w zakresie od -180 do 180.")

    if radius_km is not None and (
        not math.isfinite(radius_km) or not 0.1 <= radius_km <= 100
    ):
        raise SpatialFilterError(
            "radius_km musi mieścić się w zakresie od 0.1 do 100."
        )

    bbox_values = (min_lat, min_lon, max_lat, max_lon)
    bbox_requested = any(value is not None for value in bbox_values)

    if bbox_requested and any(value is None for value in bbox_values):
        raise SpatialFilterError(
            "Bounding box wymaga podania min_lat, min_lon, max_lat i max_lon."
        )

    if bbox_requested:
        # Powyższe sprawdzenie gwarantuje, że wartości nie są None.
        assert min_lat is not None
        assert min_lon is not None
        assert max_lat is not None
        assert max_lon is not None

        if not all(math.isfinite(value) for value in bbox_values):
            raise SpatialFilterError(
                "Współrzędne bounding boxa muszą być liczbami."
            )

        if not -90 <= min_lat < max_lat <= 90:
            raise SpatialFilterError(
                "Granice szerokości geograficznej są niepoprawne."
            )

        if not -180 <= min_lon < max_lon <= 180:
            raise SpatialFilterError(
                "Granice długości geograficznej są niepoprawne."
            )


def create_report(
    db: Session,
    report_data: ReportCreate,
    principal: Principal,
) -> Report:
    """
    Tworzy zgłoszenie. Właściciel i status pochodzą z tokenu,
    a nie z danych przesłanych przez przeglądarkę.
    """

    if principal.role == "municipal":
        user_id = None
        municipal_user_id = principal.id
        report_status = ReportStatus.FOUND_PATROL.value
        shelter_name = report_data.shelter_name
    else:
        user_id = principal.id
        municipal_user_id = None
        report_status = ReportStatus.LOST.value
        shelter_name = None

    wkt_point = (
        f"SRID=4326;POINT({report_data.longitude} {report_data.latitude})"
    )

    db_report = Report(
        title=report_data.title,
        description=report_data.description,
        coat_color=report_data.coat_color,
        breed=report_data.breed,
        sex=report_data.sex.value if report_data.sex is not None else None,
        shelter_name=shelter_name,
        species=report_data.species.value,
        status=report_status,
        photo_url=report_data.photo_url,
        contact_phone=report_data.contact_phone,
        user_id=user_id,
        municipal_user_id=municipal_user_id,
        location=WKTElement(wkt_point, srid=4326),
    )

    try:
        db.add(db_report)
        db.commit()
        db.refresh(db_report)
    except Exception:
        db.rollback()
        raise

    return db_report


def get_reports_filtered(
    db: Session,
    lat: float | None = None,
    lon: float | None = None,
    radius_km: float | None = None,
    min_lat: float | None = None,
    min_lon: float | None = None,
    max_lat: float | None = None,
    max_lon: float | None = None,
    species: Species | str | None = None,
    status: ReportStatus | str | None = None,
    limit: int = 100,
) -> list[Report]:
    """Pobiera zgłoszenia z opcjonalnymi filtrami przestrzennymi."""

    _validate_spatial_filters(
        lat=lat,
        lon=lon,
        radius_km=radius_km,
        min_lat=min_lat,
        min_lon=min_lon,
        max_lat=max_lat,
        max_lon=max_lon,
    )

    if not 1 <= limit <= 500:
        raise ValueError("limit musi mieścić się w zakresie od 1 do 500.")

    query = db.query(Report)

    if species is not None:
        query = query.filter(Report.species == _enum_value(species))

    if status is not None:
        query = query.filter(Report.status == _enum_value(status))

    if lat is not None and lon is not None and radius_km is not None:
        user_point = func.ST_SetSRID(
            func.ST_MakePoint(lon, lat),
            4326,
        )

        query = query.filter(
            func.ST_DWithin(
                cast(Report.location, Geography),
                cast(user_point, Geography),
                radius_km * 1000,
            )
        )

    if None not in (min_lat, min_lon, max_lat, max_lon):
        bbox = func.ST_MakeEnvelope(
            min_lon,
            min_lat,
            max_lon,
            max_lat,
            4326,
        )
        query = query.filter(func.ST_Intersects(Report.location, bbox))

    return (
        query
        .order_by(Report.created_at.desc(), Report.id.desc())
        .limit(limit)
        .all()
    )


def get_reports_for_principal(
    db: Session,
    principal: Principal,
) -> list[Report]:
    """Pobiera zgłoszenia aktualnie zalogowanego użytkownika."""

    query = db.query(Report)

    if principal.role == "municipal":
        query = query.filter(Report.municipal_user_id == principal.id)
    else:
        query = query.filter(Report.user_id == principal.id)

    return query.order_by(
        Report.created_at.desc(),
        Report.id.desc(),
    ).all()