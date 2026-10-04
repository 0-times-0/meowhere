from datetime import datetime
from enum import Enum
from typing import Any

from geoalchemy2.shape import to_shape
from pydantic import BaseModel, ConfigDict, Field, model_validator


class Species(str, Enum):
    CAT = "cat"
    DOG = "dog"
    OTHER = "other"


class ReportStatus(str, Enum):
    LOST = "lost"
    FOUND_PATROL = "found_patrol"
    RESOLVED = "resolved"


class AnimalSex(str, Enum):
    """
    Wartości MUSZĄ być takie same jak w frontendzie (types.ts):
    'male' | 'female' | 'unknown'.
    """

    FEMALE = "female"
    MALE = "male"
    UNKNOWN = "unknown"


def _report_payload(data: Any) -> Any:
    """
    Zamienia obiekt SQLAlchemy z geometrią PostGIS na dane,
    z których Pydantic może odczytać współrzędne.
    """

    if isinstance(data, dict):
        return data

    location = getattr(data, "location", None)
    if location is None:
        return data

    point = to_shape(location)

    return {
        "id": data.id,
        "title": data.title,
        "description": data.description,
        "coat_color": data.coat_color,
        "breed": data.breed,
        "sex": data.sex,
        "shelter_name": data.shelter_name,
        "species": data.species,
        "status": data.status,
        "photo_url": data.photo_url,
        "contact_phone": data.contact_phone,
        "user_id": data.user_id,
        "municipal_user_id": data.municipal_user_id,
        "created_at": data.created_at,
        "longitude": point.x,
        "latitude": point.y,
    }


class ReportCreate(BaseModel):
    """Dane zgłoszenia od klienta. Właściciela i status ustali backend."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    title: str = Field(min_length=3, max_length=120)
    description: str | None = Field(default=None, max_length=4000)
    coat_color: str | None = Field(default=None, max_length=80)
    breed: str | None = Field(default=None, max_length=80)
    sex: AnimalSex | None = None
    shelter_name: str | None = Field(default=None, max_length=150)

    species: Species
    photo_url: str | None = Field(default=None, max_length=255)
    contact_phone: str | None = Field(default=None, max_length=30)

    latitude: float = Field(ge=-90, le=90, allow_inf_nan=False)
    longitude: float = Field(ge=-180, le=180, allow_inf_nan=False)


class ReportSummaryResponse(BaseModel):
    """Dane do listy i mapy — bez numeru telefonu, ale z informacją o właścicielu."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    species: Species
    status: ReportStatus
    photo_url: str | None
    # Frontend wylicza z tego prawo do usunięcia/rozwiązania zgłoszenia.
    user_id: int | None = None
    municipal_user_id: int | None = None
    created_at: datetime
    latitude: float
    longitude: float

    @model_validator(mode="before")
    @classmethod
    def extract_coordinates(cls, data: Any) -> Any:
        return _report_payload(data)


class ReportResponse(ReportSummaryResponse):
    """Pełne szczegóły zgłoszenia, w tym dane kontaktowe."""

    coat_color: str | None
    breed: str | None
    sex: str | None
    shelter_name: str | None
    contact_phone: str | None