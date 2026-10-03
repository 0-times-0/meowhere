import logging
from pathlib import Path
import torch
import torchvision.models as models
from PIL import Image

from core.database import SessionLocal
from models.report import Report
from services.storage import url_to_local_path

logger = logging.getLogger("meowhere-ai")

# Inicjalizacja ResNet18 (działa płynnie na CPU)
weights = models.ResNet18_Weights.DEFAULT
model = models.resnet18(weights=weights)
model.fc = torch.nn.Identity()  # Usunięcie warstwy klasyfikacji -> wektor 512-D
model.eval()

preprocess = weights.transforms()

def get_image_embedding(image_path: Path | str) -> torch.Tensor:
    """Konwertuje zdjęcie na znormalizowany wektor cech (embedding)."""
    image = Image.open(image_path).convert("RGB")
    tensor = preprocess(image).unsqueeze(0)
    with torch.no_grad():
        embedding = model(tensor)
    return torch.nn.functional.normalize(embedding, p=2, dim=1)

def calculate_similarity(emb1: torch.Tensor, emb2: torch.Tensor) -> float:
    """Zwraca podobieństwo cosinusowe w zakresie [0.0 - 1.0]."""
    return float(torch.nn.functional.cosine_similarity(emb1, emb2).item())

def process_found_pet_ai_matching(found_report_id: int, found_photo_url: str):
    """
    Zadanie działające w tle:
    1. Pobiera zgłoszenia o statusie 'lost' z bazy PostGIS.
    2. Porównuje zdjęcie znalezionego kota ze wszystkimi zgubionymi kotami.
    """
    logger.info(f"[AI WORKER] Rozpoczynam analizę dla raportu Straży Miejskiej #ID: {found_report_id}")

    found_img_path = url_to_local_path(found_photo_url)
    if not found_img_path:
        logger.error(f"[AI WORKER] Plik dla {found_photo_url} nie istnieje na dysku.")
        return

    try:
        found_emb = get_image_embedding(found_img_path)
    except Exception as e:
        logger.error(f"[AI WORKER] Błąd przetwarzania obrazu AI: {e}")
        return

    # Otwieramy osobną sesję DB dla wątku w tle
    db = SessionLocal()
    try:
        active_lost_reports = db.query(Report).filter(
            Report.status == "lost",
            Report.photo_url.isnot(None)
        ).all()

        THRESHOLD = 0.70  # Próg 70% dopasowania

        for lost_report in active_lost_reports:
            lost_img_path = url_to_local_path(lost_report.photo_url)
            if not lost_img_path:
                continue

            try:
                lost_emb = get_image_embedding(lost_img_path)
                score = calculate_similarity(found_emb, lost_emb)

                logger.info(f"[AI WORKER] Porównanie z '{lost_report.title}' (ID {lost_report.id}): Wynik = {score:.4f}")

                if score >= THRESHOLD:
                    logger.warning(
                        f"🚨 [ALARM DOPASOWANIA AI!] Zgłoszenie Straży #{found_report_id} pasuje do zaginionego: "
                        f"'{lost_report.title}' (ID: {lost_report.id}) na {score * 100:.1f}%!\n"
                        f"Telefon do właściciela: {lost_report.contact_phone} | Zdjęcie: {lost_report.photo_url}"
                    )
            except Exception as e:
                logger.error(f"[AI WORKER] Błąd porównania ze zgłoszeniem ID {lost_report.id}: {e}")
    finally:
        db.close()
