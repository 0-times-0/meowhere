from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=80, example="jan_kowalski")
    email: str = Field(..., example="jan@example.com")
    full_name: str = Field(..., max_length=120, example="Jan Kowalski")
    phone_number: Optional[str] = Field(None, max_length=30, example="+48123456789")
    is_active: bool = True
    is_verified: bool = False


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, example="supersecret123")


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MunicipalUserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=80, example="sluzba_miejska")
    email: str = Field(..., example="sluzba@miasto.pl")
    full_name: str = Field(..., max_length=120, example="Straż Miejska")
    phone_number: Optional[str] = Field(None, max_length=30, example="+48111222333")
    department: Optional[str] = Field(None, max_length=120, example="Dział opieki nad zwierzętami")
    shelter_name: Optional[str] = Field(None, max_length=150, example="Schronisko przy ul. Zielonej 12")
    shelter_address: Optional[str] = Field(None, max_length=255, example="ul. Zielona 12, 00-001 Miasto")
    is_active: bool = True
    is_verified: bool = False


class MunicipalUserCreate(MunicipalUserBase):
    password: str = Field(..., min_length=8, example="supersecret123")


class MunicipalUserResponse(MunicipalUserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
