import math
from typing import Any

from geoalchemy2.shape import to_shape
from sqlalchemy.orm import Session

from models.report import Report


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_earth_km = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(d_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2.0) ** 2
    )
    return 2.0 * radius_earth_km * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))


def _lat_lon(report: Report) -> tuple[float, float] | None:
    """
    Wyciąga (szerokość, długość) z geometrii PostGIS.

    Model Report NIE ma kolumn latitude/longitude — jest tylko `location`
    (POINT, SRID 4326). Wcześniejsza wersja czytała nieistniejące
    atrybuty i kończyła się błędem 500.
    """

    location = getattr(report, "location", None)
    if location is None:
        return None

    try:
        point = to_shape(location)
    except Exception:
        return None

    return float(point.y), float(point.x)


def _tokens(text: str | None) -> set[str]:
    if not text:
        return set()
    cleaned = "".join(ch.lower() if ch.isalnum() else " " for ch in text)
    return {word for word in cleaned.split() if len(word) >= 3}


def find_matches_for_report(
    db: Session,
    report: Report,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """
    Szuka kontr-zgłoszeń: dla 'lost' pokazuje 'found_patrol' i odwrotnie.
    Ocena = gatunek + odległość + umaszczenie + rasa + płeć + opis.
    """

    if report.status == "lost":
        target_status = "found_patrol"
    elif report.status == "found_patrol":
        target_status = "lost"
    else:
        # Zgłoszenie rozwiązane nie potrzebuje dopasowań.
        return []

    candidates = (
        db.query(Report)
        .filter(
            Report.id != report.id,
            Report.species == report.species,
            Report.status == target_status,
        )
        .order_by(Report.created_at.desc())
        .limit(100)
        .all()
    )

    base_coords = _lat_lon(report)
    base_color = _tokens(report.coat_color)
    base_breed = _tokens(report.breed)
    base_desc = _tokens(f"{report.title or ''} {report.description or ''}")

    results: list[dict[str, Any]] = []

    for candidate in candidates:
        score = 0.35
        reasons: list[str] = ["Ten sam gatunek"]

        candidate_coords = _lat_lon(candidate)

        dist_km: float | None = None
        if base_coords is not None and candidate_coords is not None:
            dist_km = _haversine_km(
                base_coords[0],
                base_coords[1],
                candidate_coords[0],
                candidate_coords[1],
            )
            if dist_km <= 2.0:
                score += 0.30
                reasons.append(f"Bardzo blisko ({dist_km:.1f} km)")
            elif dist_km <= 8.0:
                score += 0.20
                reasons.append(f"W tej samej okolicy ({dist_km:.1f} km)")
            elif dist_km <= 20.0:
                score += 0.10
                reasons.append(f"W zasięgu miasta ({dist_km:.1f} km)")

        cand_color = _tokens(candidate.coat_color)
        if base_color and cand_color and (base_color & cand_color):
            score += 0.20
            reasons.append("Zgodne umaszczenie")

        cand_breed = _tokens(candidate.breed)
        if base_breed and cand_breed and (base_breed & cand_breed):
            score += 0.10
            reasons.append("Podobna rasa / typ")

        if (
            report.sex
            and candidate.sex
            and report.sex != "unknown"
            and candidate.sex != "unknown"
            and report.sex == candidate.sex
        ):
            score += 0.05
            reasons.append("Zgodna płeć")

        cand_desc = _tokens(f"{candidate.title or ''} {candidate.description or ''}")
        common_words = base_desc & cand_desc
        if common_words:
            score += min(0.10, 0.03 * len(common_words))

        final_score = round(min(score, 0.99), 2)
        if final_score >= 0.40:
            results.append(
                {
                    "report_id": candidate.id,
                    "title": candidate.title,
                    "species": candidate.species,
                    "status": candidate.status,
                    "coat_color": candidate.coat_color,
                    "breed": candidate.breed,
                    "shelter_name": candidate.shelter_name,
                    "photo_url": candidate.photo_url,
                    "latitude": candidate_coords[0] if candidate_coords else None,
                    "longitude": candidate_coords[1] if candidate_coords else None,
                    "distance_km": round(dist_km, 2) if dist_km is not None else None,
                    "similarity_score": final_score,
                    "reasons": reasons,
                }
            )

    results.sort(
        key=lambda item: (
            item["similarity_score"],
            -(item["distance_km"] if item["distance_km"] is not None else 999.0),
        ),
        reverse=True,
    )
    return results[:limit]