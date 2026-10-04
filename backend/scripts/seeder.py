"""Wypełnia bazę danymi demonstracyjnymi (konta + przykładowe zgłoszenia).

Uruchomienie:
    sudo docker compose exec backend python scripts/seeder.py

Skrypt jest idempotentny: można go uruchamiać wielokrotnie.
Hasła kont demo są przy każdym uruchomieniu ustawiane na wartości
z konfiguracji, żeby logowanie zawsze działało tak, jak w dokumentacji.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from geoalchemy2.elements import WKTElement
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from core.config import settings
from core.database import Base, SessionLocal, engine
from core.security import hash_password
from models import MunicipalUser, Report, User


RESIDENT_EMAIL = "anna.kowalska@example.com"
RESIDENT_USERNAME = "anna_kowalska"
RESIDENT_PASSWORD = "Mieszkaniec123!"


def _ensure_resident(db: Session) -> User:
    resident = (
        db.query(User)
        .filter(func.lower(User.email) == RESIDENT_EMAIL)
        .first()
    )

    if resident is None:
        resident = User(
            username=RESIDENT_USERNAME,
            email=RESIDENT_EMAIL,
            full_name="Anna Kowalska",
            phone_number="+48 501 234 567",
            password_hash=hash_password(RESIDENT_PASSWORD),
            is_active=True,
            is_verified=True,
        )
        db.add(resident)
        db.flush()
        print(f"[+] Utworzono konto mieszkańca: {RESIDENT_EMAIL}")
    else:
        resident.password_hash = hash_password(RESIDENT_PASSWORD)
        db.flush()
        print(f"[=] Konto mieszkańca już istnieje: {RESIDENT_EMAIL}")

    return resident


def _ensure_municipal(db: Session) -> MunicipalUser:
    """
    Numer odznaki jest przechowywany w kolumnie `username`
    (model MunicipalUser nie ma osobnego pola badge_number).
    """

    badge = settings.DEMO_MUNICIPAL_BADGE

    officer = (
        db.query(MunicipalUser)
        .filter(func.lower(MunicipalUser.username) == badge.lower())
        .first()
    )

    if officer is None:
        officer = MunicipalUser(
            username=badge,
            email=settings.DEMO_MUNICIPAL_EMAIL,
            full_name=settings.DEMO_MUNICIPAL_NAME,
            department=settings.DEMO_MUNICIPAL_UNIT,
            shelter_name="Schronisko na Paluchu",
            password_hash=hash_password(settings.DEMO_MUNICIPAL_PASSWORD),
            is_active=True,
            is_verified=True,
        )
        db.add(officer)
        db.flush()
        print(f"[+] Utworzono konto Straży Miejskiej: {badge}")
    else:
        officer.password_hash = hash_password(settings.DEMO_MUNICIPAL_PASSWORD)
        db.flush()
        print(f"[=] Konto Straży Miejskiej już istnieje: {badge}")

    return officer


def _seed_reports(db: Session, resident: User, officer: MunicipalUser) -> None:
    if db.query(Report).count() > 0:
        print("[=] Zgłoszenia już są w bazie - pomijam przykłady.")
        return

    db.add_all(
        [
            Report(
                title="Zaginął rudy kot Karmel",
                description="Rudy pręgowany kocur z białym krawatem, bardzo łagodny.",
                species="cat",
                status="lost",
                coat_color="rudy z białym",
                breed="Europejski",
                sex="male",
                contact_phone="+48 501 234 567",
                user_id=resident.id,
                location=WKTElement("SRID=4326;POINT(21.0122 52.2297)", srid=4326),
            ),
            Report(
                title="Odłowiono rudego kota na Śródmieściu",
                description="Kot znaleziony w okolicy ul. Marszałkowskiej, bez obroży.",
                species="cat",
                status="found_patrol",
                coat_color="rudy pręgowany",
                breed="Europejski",
                sex="male",
                shelter_name="Schronisko na Paluchu",
                contact_phone="+48 22 986 00 00",
                municipal_user_id=officer.id,
                location=WKTElement("SRID=4326;POINT(21.0155 52.2315)", srid=4326),
            ),
            Report(
                title="Zaginęła suczka Luna (beagle)",
                description="Pobiegła za wiewiórką w Parku Skaryszewskim. Ma czerwoną obrożę.",
                species="dog",
                status="lost",
                coat_color="trikolor (brązowo-biało-czarny)",
                breed="Beagle",
                sex="female",
                contact_phone="+48 501 234 567",
                user_id=resident.id,
                location=WKTElement("SRID=4326;POINT(21.0558 52.2412)", srid=4326),
            ),
        ]
    )
    print("[+] Dodano 3 przykładowe zgłoszenia.")


def seed() -> None:
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        resident = _ensure_resident(db)
        officer = _ensure_municipal(db)
        _seed_reports(db, resident, officer)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    print()
    print("Seeder zakończony sukcesem.")
    print(f"Mieszkaniec:    {RESIDENT_EMAIL} / {RESIDENT_PASSWORD}")
    print(
        f"Straż Miejska: {settings.DEMO_MUNICIPAL_BADGE} / "
        f"{settings.DEMO_MUNICIPAL_PASSWORD}"
    )


if __name__ == "__main__":
    seed()