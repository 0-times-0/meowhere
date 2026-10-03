from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from core.database import Base


class MunicipalUser(Base):
    __tablename__ = "municipal_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(120), nullable=False)
    password_hash = Column(String(255), nullable=False)
    phone_number = Column(String(30), nullable=True)
    department = Column(String(120), nullable=True)
    shelter_name = Column(String(150), nullable=True)
    shelter_address = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    reports = relationship(
        "Report",
        back_populates="creator_municipal_user",
        foreign_keys="Report.municipal_user_id",
        cascade="all, delete-orphan",
    )
