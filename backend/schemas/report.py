from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, model_validator
from shapely import wkb

class ReportBase(BaseModel):
    title: str = Field(..., max_length=120, example="Zaginął kot")
    description: Optional[str] = Field(None, example="Białe łapki, reaguje na imię Loszka")
    coat_color: Optional[str] = Field(None, example="biało-czarny")
    breed: Optional[str] = Field(None, example="kot domowy")
    sex: Optional[str] = Field(None, example="samica")
    species: str = Field(..., example="cat")
    status: str = Field(..., example="lost")
    photo_url: Optional[str] = Field(None, example="https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba")
    contact_phone: Optional[str] = Field(None, example="+48123456789")

class ReportCreate(ReportBase):
    latitude: float = Field(..., ge=-90, le=90, example=50.0614)
    longitude: float = Field(..., ge=-180, le=180, example=19.9366)

class ReportResponse(ReportBase):
    id: int
    created_at: datetime
    latitude: float
    longitude: float

    class Config:
        from_attributes = True

    @model_validator(mode="wrap")
    @classmethod
    def extract_coordinates(cls, data, handler):
        # Jeśli dane pochodzą z modelu SQLAlchemy z kolumną Geometry
        if hasattr(data, "location") and data.location is not None:
            point = wkb.loads(bytes(data.location.data))
            return handler({
                "id": data.id,
                "title": data.title,
                "description": data.description,
                "coat_color": data.coat_color,
                "breed": data.breed,
                "sex": data.sex,
                "species": data.species,
                "status": data.status,
                "photo_url": data.photo_url,
                "contact_phone": data.contact_phone,
                "created_at": data.created_at,
                "longitude": point.x,
                "latitude": point.y
            })
        return handler(data)