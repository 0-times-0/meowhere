### 1. Uruchomienie kontenerów
```bash
docker compose up -d --build
```

### 2.Zasilenie bazy danymi demonstracyjnymi
```bash
docker compose exec backend python -m scripts.seeder
```

### 3. Dostęp lokalny
Swagger UI dokumentacja API: http://localhost:8000/docs
Healthcheck: http://localhost:8000/health

### 4. Endpointy API

Przykładowy payload JSON:
```bash
{
  "title": "Zaginął kot",
  "description": "Białe łapki, reaguje na imię Mruczek",
  "species": "cat",
  "status": "lost",
  "latitude": 50.0614,
  "longitude": 19.9366,
  "photo_url": "[https://example.com/foto.jpg](https://example.com/foto.jpg)",
  "contact_phone": "+48123456789"
}
```

POST /reports/
GET /reports/

Przykładowy format odpowiedzi 
```bash
[
  {
    "id": 1,
    "title": "Zaginął pies: Mariusz",
    "description": "Czarny labrador",
    "species": "dog",
    "status": "lost",
    "photo_url": "[https://example.com/pies.jpg](https://example.com/pies.jpg)",
    "contact_phone": "+48123456789",
    "latitude": 50.0442,
    "longitude": 20.0121,
    "created_at": "2026-10-03T14:20:00"
  }
]
```

