from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr


AccountRole = Literal["resident", "municipal"]


class AuthUser(BaseModel):
    """Minimalny profil zwracany po zalogowaniu (kontrakt frontendu)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    full_name: str
    phone_number: str | None = None


class ResidentLoginRequest(BaseModel):
    """Logowanie mieszkańca: e-mail (lub nazwa użytkownika) + hasło."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    email: EmailStr
    password: SecretStr


class ResidentRegisterRequest(BaseModel):
    """Rejestracja mieszkańca — bez pól roli/uprawnień."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    email: EmailStr
    password: SecretStr
    full_name: str = Field(min_length=2, max_length=120)
    phone_number: str | None = Field(default=None, max_length=30)


class MunicipalLoginRequest(BaseModel):
    """Logowanie Straży Miejskiej: numer odznaki + hasło."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    badge_number: str = Field(min_length=2, max_length=80)
    password: SecretStr


class ResidentAuthResponse(BaseModel):
    """Odpowiedź po zalogowaniu/rejestracji mieszkańca."""

    access_token: str
    token_type: Literal["bearer"] = "bearer"
    role: Literal["resident"] = "resident"
    user: AuthUser


class MunicipalAuthResponse(BaseModel):
    """Odpowiedź po zalogowaniu pracownika straży."""

    access_token: str
    token_type: Literal["bearer"] = "bearer"
    role: Literal["municipal"] = "municipal"
    municipal_user: AuthUser


class UserCreate(BaseModel):
    """Dane do rejestracji mieszkańca. Nie przyjmuje pól ról ani uprawnień."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    username: str = Field(
        min_length=3,
        max_length=80,
        pattern=r"^[a-zA-Z0-9_.-]+$",
        examples=["jan_kowalski"],
    )
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=120)
    phone_number: str | None = Field(default=None, max_length=30)
    password: SecretStr = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    """Publiczne dane mieszkańca — bez hasła i jego hasha."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    full_name: str
    phone_number: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class MunicipalUserResponse(BaseModel):
    """Dane pracownika straży — bez hasła i jego hasha."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    full_name: str
    phone_number: str | None
    department: str | None
    shelter_name: str | None
    shelter_address: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class TokenResponse(BaseModel):
    """Odpowiedź po poprawnym logowaniu (formularz OAuth2)."""

    access_token: str
    token_type: Literal["bearer"] = "bearer"
    role: AccountRole
    username: str


class PrincipalResponse(BaseModel):
    """Minimalne informacje o aktualnie zalogowanym koncie."""

    id: int
    username: str
    role: AccountRole