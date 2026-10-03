from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import cast, func
from geoalchemy2.elements import WKTElement
from geoalchemy2.types import Geography
from models.report import Report
from schemas.report import ReportCreate

def create_report(db: Session, report_data: ReportCreate) -> Report:
    #PostGIS w standardzie WKT: POINT(longitude latitude) -> (X Y)
    wkt_point = f"SRID=4326;POINT({report_data.longitude} {report_data.latitude})"
    db_report = Report(
        title=report_data.title,
        description=report_data.description,
        coat_color=report_data.coat_color,
        breed=report_data.breed,
        sex=report_data.sex,
        shelter_name=report_data.shelter_name,
        user_id=report_data.user_id,
        municipal_user_id=report_data.municipal_user_id,
        species=report_data.species,
        status=report_data.status,
        photo_url=report_data.photo_url,
        contact_phone=report_data.contact_phone,
        location=WKTElement(wkt_point, srid=4326)
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

def get_reports_filtered(
    db: Session,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    radius_km: Optional[float] = None,
    min_lat: Optional[float] = None,
    min_lon: Optional[float] = None,
    max_lat: Optional[float] = None,
    max_lon: Optional[float] = None,
    species: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100
) -> List[Report]:
    query = db.query(Report)

    if species:
        query = query.filter(Report.species == species)
    if status:
        query = query.filter(Report.status == status)

    # 1. Filtrowanie po promieniu (ST_DWithin na Geography liczy w metrach)
    if lat is not None and lon is not None and radius_km is not None:
        user_point = func.ST_SetSRID(func.ST_MakePoint(lon, lat), 4326)
        radius_meters = radius_km * 1000.0
        query = query.filter(
            func.ST_DWithin(
                cast(Report.location, Geography),
                cast(user_point, Geography),
                radius_meters
            )
        )

    # 2. Filtrowanie Bounding Box
    elif None not in (min_lat, min_lon, max_lat, max_lon):
        bbox = func.ST_MakeEnvelope(min_lon, min_lat, max_lon, max_lat, 4326)
        query = query.filter(func.ST_Intersects(Report.location, bbox))

    return query.order_by(Report.created_at.desc()).limit(limit).all()