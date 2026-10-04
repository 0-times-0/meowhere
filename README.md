<div align="center">

# 🐾 MEOWHERE

### Znajdźmy je razem.

Mapa, którą widzą wszyscy — mieszkańcy i Straż Miejska w jednym miejscu.
Zgłoszenie zaginięcia w pół minuty. Dopasowanie, które znajduje algorytm.

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15%20%2B%20PostGIS-4169E1?logo=postgresql&logoColor=white)](https://postgis.net/)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-6-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-8-646CFF?logo=vite&logoColor=white)](https://vite.dev/)
[![Leaflet](https://img.shields.io/badge/Leaflet-1.9-199900?logo=leaflet&logoColor=white)](https://leafletjs.com/)
[![Docker](https://img.shields.io/badge/Docker%20Compose-3%20kontenery-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose/)

**Uruchomienie** · [Funkcje](#-funkcje) · [Jak to działa](#-jak-to-działa) · [Architektura](#-architektura) · [API](#-api) · [Roadmapa](#-roadmapa)

</div>

---

## 💡 Problem

Gdy ginie zwierzę, czas gra przeciwko nam. Informacja rozjeżdża się po grupach na Facebooku, ogłoszeniach na słupach i telefonach do schronisk. Straż Miejska odławia zwierzę i zapisuje to w swoim systemie. Dwie instytucje, dwa zbiory danych i jedno zwierzę, które jest w obu — ale nikt o tym nie wie.

**MEOWHERE to jedna wspólna mapa.** Mieszkaniec zgłasza zaginięcie, Eko-Patrol zgłasza odłowienie — a system sam wskazuje, że te dwa zgłoszenia dotyczą prawdopodobnie tego samego zwierzaka.

---

## ✨ Funkcje

<table>
<tr>
<td width="50%" valign="top">

### 👤 Dla mieszkańców

- 🗺️ **Zgłoszenie w 30 sekund** — klik na mapie, zdjęcie, gotowe
- 📸 **Zdjęcia z walidacją** — JPG/PNG/WEBP, sprawdzana zawartość pliku, nie tylko rozszerzenie
- 🔔 **Dopasowania AI** — gdy Straż zabezpieczy zwierzę pasujące do Twojego zgłoszenia, zobaczysz je od razu, z wyjaśnieniem *dlaczego* pasuje
- 📍 **Filtry przestrzenne** — gatunek, status i promień w kilometrach od punktu na mapie
- 🙋 **„Tylko moje zgłoszenia"** — własne wpisy pod kontrolą, z możliwością zamknięcia sprawy

</td>
<td width="50%" valign="top">

### 🛡️ Dla Straży Miejskiej / Eko-Patrolu

- 🗺️ **Ta sama mapa** co mieszkańcy — koniec z rozjechanymi bazami
- 🚔 **Raporty interwencyjne** — status „odłowione", placówka docelowa, dane kontaktowe jednostki
- ✅ **Zamykanie spraw** — oznaczanie jako rozwiązane po przekazaniu zwierzęcia właścicielowi
- 📊 **Widok operacyjny** — wszystkie zgłoszenia mieszkańców + własne, z filtrami

</td>
</tr>
</table>

### 🔧 Pod maską

- **PostGIS od podszewki** — promień liczony w **metrach** (`ST_DWithin` na typie `geography`), bounding box (`ST_MakeEnvelope`), geometria w SRID 4326
- **Wyjaśnialne dopasowania** — algorytm nie zwraca „magicznego procentu", tylko listę powodów: *„Ten sam gatunek", „W tej samej okolicy (3.9 km)", „Zgodne umaszczenie"*
- **Bezpieczeństwo po stronie serwera** — status zgłoszenia i właściciel wynikają z **tokenu JWT**, nie z danych przysłanych przez przeglądarkę; nie da się tego podrobić z formularza
- **Dwie role, jedno konto wielokrotnego użytku** — mieszkańcy (`users`) i funkcjonariusze (`municipal_users`) w rozdzielonych tabelach, jeden mechanizm uwierzytelniania
- **Zero CORS-owych niespodzianek** — frontend rozmawia z API przez ścieżki względne, proxy Vite przekazuje je do backendu; przeglądarka widzi jeden origin
- **Seeder idempotentny** — dane demo można wgrać wielokrotnie bez duplikatów

---

## 🤖 Jak to działa

### Dopasowanie zgłoszeń

Zgłoszenie **zaginięcia** (`lost`) szuka wśród **odłowień** (`found_patrol`) — i odwrotnie. Ten sam gatunek to warunek wejścia, resztę waży algorytm:

| Kryterium | Waga | Przykład uzasadnienia |
|---|---:|---|
| Ten sam gatunek | +0.35 | *bazowy warunek* |
| Odległość ≤ 2 km | +0.30 | „Bardzo blisko (1.2 km)" |
| Odległość ≤ 8 km | +0.20 | „W tej samej okolicy (3.9 km)" |
| Odległość ≤ 20 km | +0.10 | „W zasięgu miasta (14.5 km)" |
| Zgodne umaszczenie | +0.20 | „Zgodne umaszczenie" |
| Podobna rasa / typ | +0.10 | „Podobna rasa / typ" |
| Zgodna płeć | +0.05 | „Zgodna płeć" |
| Wspólne słowa w opisie | +0.03 / słowo (maks. +0.10) | — |

Wyniki poniżej progu **0.40** nie są pokazywane — lepiej nie pokazać nic niż wprowadzić w błąd.

### Wyszukiwanie przestrzenne

```
GET /api/reports/?lat=52.2297&lon=21.0122&radius_km=5&species=cat&status=found_patrol
```

Serwer waliduje każdy parametr (zakresy geograficzne, spójność promienia i bounding boxa), a zapytanie leci do PostGIS-a z indeksem przestrzennym.

---

## 🏗 Architektura

```
                        ┌──────────────────────────────┐
                        │        PRZEGLĄDARKA          │
                        └───────────────┬──────────────┘
                                        │ http://localhost:5173
                        ┌───────────────▼──────────────┐
                        │   meowhere_web (Vite dev)    │
                        │   React 19 + Leaflet         │
                        └───────────────┬──────────────┘
                                        │ /api/* i /uploads/*  (proxy)
                        ┌───────────────▼──────────────┐
                        │   meowhere_api (FastAPI)     │
                        │   JWT · walidacja · PostGIS  │
                        └───────────────┬──────────────┘
                                        │ SQLAlchemy 2
                        ┌───────────────▼──────────────┐
                        │  meowhere_postgis (PG 15)    │
                        │  + rozszerzenie PostGIS 3.3  │
                        └──────────────────────────────┘
```

| Kontener | Rola | Port |
|---|---|---|
| `meowhere_web` | Frontend (Vite, HMR) | **5173** |
| `meowhere_api` | REST API, JWT, logika biznesowa | **8000** |
| `meowhere_postgis` | Baza z rozszerzeniem PostGIS | **5432** |

---

## 🧰 Stack technologiczny

| Warstwa | Technologie |
|---|---|
| **Backend** | Python 3.11 · FastAPI · SQLAlchemy 2 · Pydantic v2 · PyJWT · pwdlib (Argon2) |
| **Baza danych** | PostgreSQL 15 · PostGIS 3.3 · GeoAlchemy2 · Shapely |
| **Frontend** | React 19 · TypeScript · Vite · React Router · Leaflet / React-Leaflet · Oxlint |
| **Infrastruktura** | Docker · Docker Compose · uvicorn |
| **Jakość** | walidacja Pydantic (zakazy `extra`), testowanie nagłówków plików (magic bytes), rozdzielenie schematów publiczny/pełny |

---

## 🚀 Uruchomienie projektu

### Wymagania

- **Docker + Docker Compose** (na tym hoście: przez `sudo docker compose ...`)
- Wolne porty: **5173** (frontend), **8000** (API), **5432** (baza)
- Node.js **nie jest potrzebny na hoście** — frontend chodzi w kontenerze

```bash
sudo lsof -i :5173 -i :8000 -i :5432    # sprawdź, czy porty są wolne
```

### 1️⃣ Pierwsze uruchomienie

```bash
cd ~/Projects/meowhere/meowhere               # katalog z docker-compose.yml

sudo docker compose up -d --build             # pierwszy build: 2–4 minuty
sudo docker compose ps                        # trzy kontenery, wszystkie "Up"

sudo docker compose exec backend python scripts/seeder.py   # dane demo
```

Wynik `docker compose ps` powinien wyglądać tak:

```
meowhere_api       ... Up   0.0.0.0:8000->8000/tcp     ← backend
meowhere_postgis   ... Up   0.0.0.0:5432->5432/tcp     ← baza
meowhere_web       ... Up   0.0.0.0:5173->5173/tcp     ← frontend
```

Seeder wypisze na końcu loginy i hasła obu kont demo.

### 2️⃣ Otwórz aplikację

| Gdzie | Adres |
|---|---|
| 🗺️ **Aplikacja** | **http://localhost:5173/** |
| 📚 Dokumentacja API (Swagger) | **http://localhost:8000/docs** |
| ❤️ Health check | http://localhost:8000/health |

### Konta demo

| Rola | Login | Hasło |
|---|---|---|
| 👤 Mieszkaniec | `anna.kowalska@example.com` | `Mieszkaniec123!` |
| 🛡️ Straż Miejska | `SM-101` | `StrazMiejska123!` |

### 3️⃣ Sprawdź, że wszystko gra (30 sekund)

```bash
curl -s -o /dev/null -w 'API          -> %{http_code}\n' http://localhost:8000/health
curl -s -o /dev/null -w 'Swagger      -> %{http_code}\n' http://localhost:8000/docs
curl -s -o /dev/null -w 'Frontend     -> %{http_code}\n' http://localhost:5173/
curl -s -o /dev/null -w 'Proxy → API  -> %{http_code}\n' http://localhost:5173/api/reports
```

Oczekiwane: `200`, `200`, `200`, `200` lub `307`. Jeśli czwarty test zwraca `502`, frontend nie dosięga backendu — patrz punkt 5.

### 4️⃣ Codzienna praca

| Chcę… | Komenda |
|---|---|
| uruchomić projekt | `sudo docker compose up -d` |
| zrestartować wszystko | `sudo docker compose restart` |
| zrestartować sam frontend | `sudo docker compose restart frontend` |
| przebudować po zmianie kodu backendu | `sudo docker compose up -d --build backend` |
| podejrzeć logi | `sudo docker compose logs -f backend` |
| wejść do kontenera | `sudo docker compose exec backend bash` |
| zatrzymać (dane zostają) | `sudo docker compose stop` |
| usunąć kontenery | `sudo docker compose down` |

> ⚠️ `down` usuwa kontenery — **zdjęcia z `/app/uploads` przepadną**, jeśli nie dodałeś wolumenu (patrz sekcja *Konfiguracja*). Zgłoszenia w bazie zostają, bo baza trzyma dane w wolumenie `pgdata`.

### 5️⃣ Najczęstsze problemy przy starcie

| Objaw | Przyczyna | Naprawa |
|---|---|---|
| `address already in use` na 5173 | działa jeszcze Vite z hosta | `sudo fuser -k 5173/tcp` → `sudo docker compose up -d frontend` |
| W `ps` brak mapowania portu przy `meowhere_web` | brak `ports:` w bloku `frontend` (albo złe wcięcie) | popraw YAML → `sudo docker compose up -d --force-recreate frontend` |
| Strona się otwiera, ale jest **biała** | błąd JS w przeglądarce (często `import` typów) | F12 → Console; szczegóły w tabeli poniżej |
| `/api/...` zwraca **502** | proxy Vite nie trafia w backend | sprawdź `VITE_API_TARGET=http://backend:8000` w compose |
| Logowanie zwraca **500** | brak klucza JWT w konfiguracji | `sudo docker compose exec backend python -c "from core.config import settings; print(len(settings.signing_key))"` |
| Stara sesja / dziwne 401 | token sprzed zmiany `JWT_SECRET_KEY` | F12 → Local Storage → usuń `meowhere_auth_session` → `Ctrl+Shift+R` |

📖 **Pełny troubleshooting (8 przypadków + testy `curl`)** → [`README-dev.md`](README-dev.md)

### 6️⃣ Wariant awaryjny: frontend bez kontenera

Gdyby Docker miał problem z trzecią usługą, frontend można odpalić na hoście:

```bash
cd meowhere_frontend
npm install
npm run dev          # → http://localhost:5173
```

W tym trybie proxy `vite.config.ts` celuje w `http://localhost:8000` (backend z Dockera ma ten port opublikowany).

---

## 🖼 Zrzuty ekranu

> Podmień pliki w katalogu `docs/` na własne zrzuty (nazwy poniżej).

| Mapa i lista zgłoszeń | Szczegóły z dopasowaniami AI | Formularz zgłoszenia |
|---|---|---|
| ![Mapa](docs/screenshot-mapa.png) | ![Dopasowania](docs/screenshot-dopasowania.png) | ![Formularz](docs/screenshot-formularz.png) |

---

## 📖 Trasy aplikacji

| Trasa | Widok |
|---|---|
| `/` | Mapa + lista zgłoszeń z filtrami |
| `/search` | Wyszukiwarka przestrzenna |
| `/post` | Formularz nowego zgłoszenia *(wymaga zalogowania)* |
| `/listing?id=1` | Szczegóły zgłoszenia + sugerowane dopasowania |

---

## 🔌 API

Pełna, interaktywna dokumentacja: **http://localhost:8000/docs**

| Metoda | Endpoint | Opis | Auth |
|---|---|:---|:---:|
| `POST` | `/api/auth/resident/register` | Rejestracja mieszkańca (od razu zwraca token) | — |
| `POST` | `/api/auth/resident/login` | Logowanie mieszkańca | — |
| `POST` | `/api/auth/municipal/login` | Logowanie Straży Miejskiej (numer odznaki) | — |
| `GET` | `/api/auth/me` | Kim jestem | 🔒 |
| `GET` | `/api/reports/` | Lista i filtry (gatunek, status, promień, bbox) | — |
| `GET` | `/api/reports/mine` | Moje zgłoszenia | 🔒 |
| `GET` | `/api/reports/{id}` | Szczegóły zgłoszenia | — |
| `GET` | `/api/reports/{id}/matches` | Sugerowane dopasowania | — |
| `POST` | `/api/reports/` | Nowe zgłoszenie | 🔒 |
| `PATCH` | `/api/reports/{id}/resolve` | Oznacz jako rozwiązane | 🔒 |
| `DELETE` | `/api/reports/{id}` | Usuń zgłoszenie | 🔒 |
| `POST` | `/api/uploads/` | Wgranie zdjęcia (≤ 5 MB) | 🔒 |

---

## 🔐 Model uprawnień

| Akcja | Mieszkaniec | Straż Miejska |
|---|:---:|:---:|
| Przeglądanie mapy i listy | ✔ | ✔ |
| Dodanie zgłoszenia | ✔ (`lost`) | ✔ (`found_patrol`) |
| Oznaczenie jako rozwiązane | ✔ *(swojego)* | ✔ *(dowolnego)* |
| Usunięcie zgłoszenia | ✔ *(swojego)* | ✔ *(swojego)* |

Status i właściciel nadawane są na serwerze na podstawie tokenu — żądanie z przeglądarki nie może ich podmienić.

---

## 🗂 Struktura projektu

```
meowhere/
├── backend/
│   ├── api/          # auth · reports · uploads  (endpointy)
│   ├── core/         # config · database · security  (JWT, hasła, sesje)
│   ├── models/       # User · MunicipalUser · Report (geometria POINT 4326)
│   ├── schemas/      # kontrakty Pydantic (walidacja wejścia/wyjścia)
│   ├── services/     # spatial · storage · ai_matcher
│   └── scripts/      # seeder danych demonstracyjnych
├── meowhere_frontend/
│   └── src/
│       ├── components/   # MapView ·…
│       ├── pages/        # HomePage · CreateReportPage · ReportDetailsPage
│       ├── api.ts        # klient API
│       └── types.ts      # typy współdzielone
└── docker-compose.yml
```

---

## 🗺 Roadmapa

- [x] Wspólna mapa mieszkańców i Straży Miejskiej
- [x] Uwierzytelnianie JWT z rozdzielonymi rolami
- [x] Wyszukiwanie przestrzenne PostGIS
- [x] Dopasowania zgłoszeń z wyjaśnieniami
- [x] Upload zdjęć z walidacją zawartości
- [ ] Powiadomienia o nowym dopasowaniu (e-mail / push)
- [ ] Wersja PWA z powiadomieniami na telefonie
- [ ] Geokodowanie adres → współrzędne (wpisanie ulicy zamiast klikania)
- [ ] Panel statystyk dla Straży Miejskiej (skuteczność, czasy reakcji)
- [ ] Integracja z bazami chipów i rejestrami schronisk
- [ ] Tryb produkcyjny: statyczny build + nginx zamiast dev servera

---

## ⚙️ Konfiguracja

Kluczowe zmienne (`.env`):

```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/meowhere_db
JWT_SECRET_KEY=zmien-mnie-na-dlugii-losowy-ciag-min-32-znaki
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
UPLOAD_DIR=/app/uploads
MAX_UPLOAD_SIZE_MB=5
```

> ⚠️ Przed użyciem poza lokalnym demo **zmień `JWT_SECRET_KEY`** i dodaj wolumen na `/app/uploads`, żeby zdjęcia przetrwały przebudowę kontenerów.

---

## 🤝 Współpraca

1. Fork repozytorium
2. Gałąź: `git checkout -b feature/nazwa-funkcji`
3. Commity w konwencji `feat:`, `fix:`, `docs:`
4. Pull request z opisem zmiany

---

## 📄 Licencja

Projekt udostępniamy na licencji **MIT** — szczegóły w pliku [`LICENSE`](LICENSE).

---

<div align="center">

**MEOWHERE** — bo każde zgłoszenie to czyjeś zwierzę.

🐱 🐶 🐾

</div>
