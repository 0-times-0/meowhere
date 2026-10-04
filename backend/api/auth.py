import re

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import (
    Principal,
    create_access_token,
    get_current_principal,
    hash_password,
    verify_password,
)
from models import MunicipalUser, User
from schemas.user import (
    AuthUser,
    MunicipalAuthResponse,
    MunicipalLoginRequest,
    PrincipalResponse,
    ResidentAuthResponse,
    ResidentLoginRequest,
    ResidentRegisterRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
)


router = APIRouter(prefix="/auth", tags=["auth"])

# Znaki dozwolone w nazwie użytkownika generowanej z e-maila.
_USERNAME_SAFE = re.compile(r"[^a-z0-9_.-]")

# Minimalna długość hasła przy rejestracji (frontend waliduje to samo).
MIN_PASSWORD_LENGTH = 8


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def _email_taken(db: Session, email: str) -> bool:
    """Sprawdza e-mail w obu tabelach kont."""

    return bool(
        db.query(User.id).filter(func.lower(User.email) == email).first()
        or db.query(MunicipalUser.id)
        .filter(func.lower(MunicipalUser.email) == email)
        .first()
    )


def _username_taken(db: Session, username: str) -> bool:
    return bool(
        db.query(User.id)
        .filter(func.lower(User.username) == username)
        .first()
        or db.query(MunicipalUser.id)
        .filter(func.lower(MunicipalUser.username) == username)
        .first()
    )


def _generate_username(db: Session, email: str) -> str:
    """
    Buduje unikalną nazwę użytkownika z adresu e-mail,
    bo frontend wysyła przy rejestracji tylko e-mail.
    """

    base = _USERNAME_SAFE.sub("", email.split("@")[0].lower()) or "user"
    if len(base) < 3:
        base = f"{base}_user"

    if not _username_taken(db, base):
        return base

    for index in range(1, 1000):
        candidate = f"{base}{index}"
        if not _username_taken(db, candidate):
            return candidate

    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Nie udało się wygenerować unikalnej nazwy użytkownika.",
    )


# ----------------------------------------------------------------------
# Nowe endpointy JSON — dokładnie te, których wywołuje frontend (api.ts)
# ----------------------------------------------------------------------


@router.post("/resident/login", response_model=ResidentAuthResponse)
def resident_login(
    payload: ResidentLoginRequest,
    db: Session = Depends(get_db),
) -> ResidentAuthResponse:
    """Logowanie mieszkańca po e-mailu (lub nazwie użytkownika) i haśle."""

    identifier = str(payload.email).strip().lower()

    user = (
        db.query(User)
        .filter(
            or_(
                func.lower(User.email) == identifier,
                func.lower(User.username) == identifier,
            )
        )
        .first()
    )

    if (
        user is None
        or not user.is_active
        or not verify_password(payload.password.get_secret_value(), user.password_hash)
    ):
        raise _unauthorized("Nieprawidłowy e-mail lub hasło.")

    token = create_access_token(subject=user.id, role="resident")

    return ResidentAuthResponse(
        access_token=token,
        user=AuthUser.model_validate(user),
    )


@router.post(
    "/resident/register",
    response_model=ResidentAuthResponse,
    status_code=status.HTTP_201_CREATED,
)
def resident_register(
    payload: ResidentRegisterRequest,
    db: Session = Depends(get_db),
) -> ResidentAuthResponse:
    """Rejestruje mieszkańca i od razu zwraca token (auto-logowanie)."""

    password = payload.password.get_secret_value()
    if len(password) < MIN_PASSWORD_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Hasło musi mieć co najmniej {MIN_PASSWORD_LENGTH} znaków.",
        )

    email = str(payload.email).strip().lower()

    if _email_taken(db, email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Konto z takim adresem e-mail już istnieje.",
        )

    user = User(
        username=_generate_username(db, email),
        email=email,
        full_name=payload.full_name,
        phone_number=payload.phone_number,
        password_hash=hash_password(password),
        is_active=True,
        is_verified=True,
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Nie udało się utworzyć konta. Spróbuj innego e-maila.",
        ) from exc

    token = create_access_token(subject=user.id, role="resident")

    return ResidentAuthResponse(
        access_token=token,
        user=AuthUser.model_validate(user),
    )


@router.post("/municipal/login", response_model=MunicipalAuthResponse)
def municipal_login(
    payload: MunicipalLoginRequest,
    db: Session = Depends(get_db),
) -> MunicipalAuthResponse:
    """
    Logowanie Straży Miejskiej po numerze odznaki i haśle.

    Model MunicipalUser nie ma osobnej kolumny na numer odznaki —
    odznaka jest zapisana w polu `username` (np. "SM-101").
    """

    badge = payload.badge_number.strip().lower()

    officer = (
        db.query(MunicipalUser)
        .filter(
            or_(
                func.lower(MunicipalUser.username) == badge,
                func.lower(MunicipalUser.email) == badge,
            )
        )
        .first()
    )

    if (
        officer is None
        or not officer.is_active
        or not verify_password(
            payload.password.get_secret_value(), officer.password_hash
        )
    ):
        raise _unauthorized("Nieprawidłowy numer odznaki lub hasło.")

    token = create_access_token(subject=officer.id, role="municipal")

    return MunicipalAuthResponse(
        access_token=token,
        municipal_user=AuthUser.model_validate(officer),
    )


# ----------------------------------------------------------------------
# Endpointy pomocnicze / zgodnościowe (Swagger, OAuth2, rejestracja klasyczna)
# ----------------------------------------------------------------------


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_resident(
    user_data: UserCreate,
    db: Session = Depends(get_db),
) -> User:
    """Rejestracja z jawną nazwą użytkownika. Nie pozwala ustawiać uprawnień."""

    username = user_data.username.lower()
    email = str(user_data.email).lower()

    resident_exists = (
        db.query(User.id)
        .filter(or_(User.username == username, User.email == email))
        .first()
    )
    municipal_exists = (
        db.query(MunicipalUser.id)
        .filter(or_(MunicipalUser.username == username, MunicipalUser.email == email))
        .first()
    )

    if resident_exists or municipal_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Konto z taką nazwą użytkownika lub adresem e-mail już istnieje.",
        )

    user = User(
        username=username,
        email=email,
        full_name=user_data.full_name,
        phone_number=user_data.phone_number,
        password_hash=hash_password(user_data.password.get_secret_value()),
        is_active=True,
        is_verified=False,
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Nie udało się utworzyć konta. Sprawdź nazwę użytkownika i e-mail.",
        ) from exc

    return user


@router.post("/token", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> TokenResponse:
    """
    Logowanie formularzem OAuth2 (wygodne w Swaggerze).

    W polu `username` można podać nazwę użytkownika albo e-mail.
    """

    identifier = form_data.username.strip().lower()

    resident = (
        db.query(User)
        .filter(or_(User.username == identifier, User.email == identifier))
        .first()
    )

    if resident is not None:
        if not resident.is_active or not verify_password(
            form_data.password,
            resident.password_hash,
        ):
            raise _unauthorized("Nieprawidłowa nazwa użytkownika/e-mail lub hasło.")

        return TokenResponse(
            access_token=create_access_token(
                subject=resident.id,
                role="resident",
            ),
            role="resident",
            username=resident.username,
        )

    municipal_user = (
        db.query(MunicipalUser)
        .filter(
            or_(
                MunicipalUser.username == identifier,
                MunicipalUser.email == identifier,
            )
        )
        .first()
    )

    if municipal_user is None or not municipal_user.is_active:
        raise _unauthorized("Nieprawidłowa nazwa użytkownika/e-mail lub hasło.")

    if not verify_password(form_data.password, municipal_user.password_hash):
        raise _unauthorized("Nieprawidłowa nazwa użytkownika/e-mail lub hasło.")

    return TokenResponse(
        access_token=create_access_token(
            subject=municipal_user.id,
            role="municipal",
        ),
        role="municipal",
        username=municipal_user.username,
    )


@router.get("/me", response_model=PrincipalResponse)
def get_me(
    principal: Principal = Depends(get_current_principal),
) -> PrincipalResponse:
    """Zwraca podstawowe informacje z konta aktualnie zalogowanej osoby."""

    return PrincipalResponse(
        id=principal.id,
        username=principal.username,
        role=principal.role,
    )