from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from geoalchemy2 import Geometry
from core.database import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)
    coat_color = Column(String(80), nullable=True)
    breed = Column(String(80), nullable=True)
    sex = Column(String(30), nullable=True)
    species = Column(String(50), index=True, nullable=False)
    status = Column(String(50), index=True, nullable=False)
    photo_url = Column(String(255), nullable=True)
    contact_phone = Column(String(30), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # SRID 4326 = format WGS84 (GPS: szerokość/długość)
    location = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)