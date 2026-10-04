from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Literal

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from core.config import settings
from core.database import get_db
from models import MunicipalUser, User


PrincipalRole = Literal["resident", "municipal"]

password_hasher = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/token",
)


@dataclass(frozen=True)
class Principal:
    """Zalogowany użytkownik — mieszkaniec albo pracownik straży."""

    id: int
    role: PrincipalRole
    username: str


def hash_password(password: str) -> str:
    """Hashuje hasło przed zapisaniem go w bazie."""

    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Porównuje hasło z jego hashem zapisanym w bazie."""

    if not password_hash:
        return False

    try:
        return password_hasher.verify(password, password_hash)
    except Exception:
        # Uszkodzony/nieznany format hasha nie może wywalić endpointu.
        return False


def create_access_token(
    *,
    subject: int,
    role: PrincipalRole,
    expires_delta: timedelta | None = None,
) -> str:
    """Tworzy podpisany token dostępu JWT."""

    if expires_delta is None:
        expires_delta = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    expires_at = datetime.now(timezone.utc) + expires_delta

    payload = {
        "sub": str(subject),
        "role": role,
        "exp": expires_at,
    }

    # settings.signing_key wybiera JWT_SECRET_KEY, albo SECRET_KEY jako fallback.
    return jwt.encode(
        payload,
        settings.signing_key,
        algorithm=settings.JWT_ALGORITHM,
    )


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Brak poprawnego logowania lub token wygasł.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_principal(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Principal:
    """Weryfikuje token i pobiera aktywne konto z bazy."""

    try:
        payload = jwt.decode(
            token,
            settings.signing_key,
            algorithms=[settings.JWT_ALGORITHM],
            options={"require": ["exp", "sub", "role"]},
        )
    except jwt.InvalidTokenError as exc:
        raise _unauthorized() from exc

    subject = payload.get("sub")
    role_value = payload.get("role")

    try:
        account_id = int(subject)
    except (TypeError, ValueError) as exc:
        raise _unauthorized() from exc

    if role_value == "resident":
        account = db.get(User, account_id)
        role: PrincipalRole = "resident"
    elif role_value == "municipal":
        account = db.get(MunicipalUser, account_id)
        role = "municipal"
    else:
        raise _unauthorized()

    if account is None or not account.is_active:
        raise _unauthorized()

    return Principal(
        id=account.id,
        role=role,
        username=account.username,
    )


def require_municipal_user(
    principal: Principal = Depends(get_current_principal),
) -> Principal:
    """Ogranicza endpoint do zalogowanego pracownika straży."""

    if principal.role != "municipal":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ta funkcja jest dostępna tylko dla Straży Miejskiej.",
        )

    return principal