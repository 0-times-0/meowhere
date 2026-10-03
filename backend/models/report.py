from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from core.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(120), nullable=False)
    description = Column(Text, nullable=True)
    coat_color = Column(String(80), nullable=True)
    breed = Column(String(80), nullable=True)
    sex = Column(String(30), nullable=True)
    shelter_name = Column(String(150), nullable=True)
    species = Column(String(50), index=True, nullable=False)
    status = Column(String(50), index=True, nullable=False)
    photo_url = Column(String(255), nullable=True)
    contact_phone = Column(String(30), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    municipal_user_id = Column(Integer, ForeignKey("municipal_users.id"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    creator_user = relationship(
        "User",
        back_populates="reports",
        foreign_keys=[user_id],
    )
    creator_municipal_user = relationship(
        "MunicipalUser",
        back_populates="reports",
        foreign_keys=[municipal_user_id],
    )

    # SRID 4326 = format WGS84 (GPS: szerokość/długość)
    location = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)