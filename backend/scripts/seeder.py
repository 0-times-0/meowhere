import random
from faker import Faker
from core.database import SessionLocal, init_db
from models.report import Report
from geoalchemy2.elements import WKTElement

fake = Faker("pl_PL")

# Współrzędne Tauron Arena: 50.0680, 19.9880
CENTER_LAT = 50.0680
CENTER_LON = 19.9880

SPECIES_LIST = ["cat", "dog", "other"]
STATUS_LIST = ["lost", "found_patrol", "resolved"]

DOG_PHOTOS = [
    "https://images.unsplash.com/photo-1543466835-00a7907e9de1",
    "https://images.unsplash.com/photo-1583511655857-d19b40a7a54e",
    "https://images.unsplash.com/photo-1537151625747-768eb6cf92b2",
]
CAT_PHOTOS = [
    "https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba",
    "https://images.unsplash.com/photo-1573865526739-10659fec78a5",
    "https://images.unsplash.com/photo-1495360010541-f48722b34f7d",
]

def generate_reports(count: int = 50):
    init_db()
    db = SessionLocal()

    try:
        reports = []
        for _ in range(count):
            specie = random.choice(SPECIES_LIST)
            stat = random.choices(STATUS_LIST, weights=[60, 30, 10])[0]

            # Rozrzut w promieniu około 3-5 km od centrum
            lat_offset = random.uniform(-0.035, 0.035)
            lon_offset = random.uniform(-0.045, 0.045)
            lat = CENTER_LAT + lat_offset
            lon = CENTER_LON + lon_offset

            if specie == "dog":
                title = f"Zaginął pies: {fake.first_name()}"
                photo = random.choice(DOG_PHOTOS)
            elif specie == "cat":
                title = f"Szukamy kota: {fake.first_name()}"
                photo = random.choice(CAT_PHOTOS)
            else:
                title = "Widziano błąkające się zwierzę"
                photo = "https://images.unsplash.com/photo-1425082661705-1834bfd09dca"

            if stat == "found_patrol":
                title = f"[STRAŻ MIEJSKA] Zabezpieczono: {specie}"

            wkt_point = f"SRID=4326;POINT({lon} {lat})"

            coat_color = random.choice(["biały", "czarny", "szary", "brązowy", "rudo-bury", "pręgowane"]) if random.random() < 0.8 else None
            breed = random.choice(["kot domowy", "mieszaniec", "pies mieszany", "labrador", "owczarek niemiecki", "chihuahua"]) if random.random() < 0.7 else None
            sex = random.choice(["samiec", "samica"]) if random.random() < 0.6 else None

            report = Report(
                title=title,
                description=fake.sentence(nb_words=12),
                coat_color=coat_color,
                breed=breed,
                sex=sex,
                species=specie,
                status=stat,
                photo_url=photo,
                contact_phone=fake.phone_number() if stat == "lost" else "986",
                location=WKTElement(wkt_point, srid=4326),
                created_at=fake.date_time_this_month()
            )
            reports.append(report)

        db.add_all(reports)
        db.commit()
        print(f"Pomyślnie dodano {count} zgłoszeń demonstracyjnych do bazy.")
    except Exception as e:
        db.rollback()
        print(f"Błąd podczas seedowania bazy: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    generate_reports(50)