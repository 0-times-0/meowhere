#!/usr/bin/env bash
# ============================================================
#  MEOWHERE — sprawdzenie struktury i połączeń
#
#  Uruchom z katalogu głównego projektu (tam, gdzie docker-compose.yml):
#      bash check-structure.sh
#
#  Jeśli docker działa u ciebie bez sudo:
#      DC_CMD="docker compose" bash check-structure.sh
# ============================================================

DC="${DC_CMD:-sudo docker compose}"
PROBLEMS=$(mktemp)

problem(){ printf '  - %s\n' "$1" >> "$PROBLEMS"; }
ok()  { printf '  [OK]   %s\n' "$1"; }
bad() { printf '  [BRAK] %s\n' "$1"; problem "$1"; }

# --- znajdź katalog projektu ---
if   [ -f docker-compose.yml ];    then :
elif [ -f ../docker-compose.yml ]; then cd ..
elif [ -f ../../docker-compose.yml ]; then cd ../..
else
  echo "!! Nie widzę docker-compose.yml (sprawdzone: ., .., ../..)"
  echo "   Wejdź do katalogu projektu i uruchom ponownie."
  exit 1
fi
echo "Katalog projektu: $(pwd)"
echo

# ------------------------------------------------------------
echo "=== A. STRUKTURA KATALOGÓW ==="
for d in backend backend/api backend/services backend/scripts backend/core \
         meowhere_frontend meowhere_frontend/src meowhere_frontend/src/pages \
         meowhere_frontend/src/components; do
  if [ -d "$d" ]; then
    echo; echo "[$d]"
    ls -1 "$d" | sed 's/^/    /'
  else
    bad "brak katalogu: $d"
  fi
done

# ------------------------------------------------------------
echo; echo "=== B. PLIKI KLUCZOWE ==="
for f in \
  docker-compose.yml \
  backend/Dockerfile backend/main.py backend/requirements.txt \
  backend/core/config.py \
  backend/api/reports.py backend/api/uploads.py \
  backend/services/spatial.py backend/services/storage.py backend/services/ai_matcher.py \
  backend/scripts/seeder.py \
  meowhere_frontend/Dockerfile.dev meowhere_frontend/.dockerignore \
  meowhere_frontend/package.json meowhere_frontend/vite.config.ts meowhere_frontend/index.html \
  meowhere_frontend/src/main.tsx meowhere_frontend/src/App.tsx \
  meowhere_frontend/src/api.ts meowhere_frontend/src/types.ts \
  meowhere_frontend/src/components/MapView.tsx \
  meowhere_frontend/src/pages/HomePage.tsx \
  meowhere_frontend/src/pages/CreateReportPage.tsx \
  meowhere_frontend/src/pages/ReportDetailsPage.tsx ; do
  if [ -f "$f" ]; then ok "$f"; else bad "$f"; fi
done

for e in .env backend/.env; do
  if [ -f "$e" ]; then
    echo "  [OK]   $e  (zmienne: $(grep -oE '^[A-Za-z_][A-Za-z0-9_]*' "$e" | tr '\n' ' '))"
  fi
done

# ------------------------------------------------------------
echo; echo "=== C. DOCKER COMPOSE (po rozwinięciu) ==="
if $DC config >/tmp/meowhere_cfg 2>/tmp/meowhere_cfg_err; then
  echo "  YAML poprawny."
  echo "  Usługi: $($DC config --services | tr '\n' ' ')"
  for s in backend db frontend; do
    if $DC config --services | grep -qx "$s"; then ok "usługa $s zdefiniowana"; else bad "usługa $s BRAK w compose"; fi
  done
  echo; echo "  --- blok 'frontend' po rozwinięciu ---"
  awk '/^  [A-Za-z0-9_-]+:$/{svc=$0; gsub(/[ :]/,"",svc)} svc=="frontend"{print}' /tmp/meowhere_cfg | sed 's/^/    /'
  if grep -q "VITE_API_TARGET" /tmp/meowhere_cfg; then
    ok "VITE_API_TARGET ustawiony (proxy frontendu wie, gdzie jest backend)"
  else
    bad "brak VITE_API_TARGET w compose — proxy frontendu może nie trafić w backend"
  fi
  if grep -qE 'published: *"?5173' /tmp/meowhere_cfg; then
    ok "port 5173 opublikowany na host"
  else
    bad "port 5173 NIE jest opublikowany"
  fi
else
  bad "docker compose config zgłasza błąd:"
  sed 's/^/    /' /tmp/meowhere_cfg_err
fi

# ------------------------------------------------------------
echo; echo "=== D. KONTENERY I PORTY ==="
$DC ps
if sudo docker port meowhere_web 2>/dev/null | grep -q 5173; then
  ok "docker port meowhere_web -> 5173 zmapowany"
else
  bad "docker port meowhere_web nie pokazuje 5173"
fi

# ------------------------------------------------------------
echo; echo "=== E. POŁĄCZENIA ==="
chk(){ # $1=url  $2=oczekiwane kody
  local url="$1" expect="$2" code
  code=$(curl -s -o /dev/null --max-time 6 -w '%{http_code}' "$url" 2>/dev/null)
  printf '  %-46s HTTP %-4s' "$url" "$code"
  if printf '%s' "$expect" | tr ' ' '\n' | grep -qx "$code"; then
    echo "[OK]"
  else
    echo "[OCZEKIWANO $expect]"
    problem "połączenie: $url -> HTTP $code (oczekiwano $expect)"
  fi
}
chk "http://localhost:8000/docs"        "200"
chk "http://localhost:8000/api/reports" "200 401 403 307"
chk "http://localhost:5173/"            "200"
chk "http://localhost:5173/api/reports" "200 401 403 307"

echo; echo "  --- wewnątrz sieci docker ---"
printf '    db pg_isready            : '
$DC exec -T db pg_isready 2>/dev/null | sed 's/^/ /' || echo "(brak odpowiedzi)"
printf '    frontend -> backend:8000 : '
$DC exec -T frontend sh -c 'wget -qO- -T 5 http://backend:8000/api/reports 2>/dev/null | head -c 80' || printf 'BRAK ODPOWIEDZI'
echo
printf '    frontend -> wlasny proxy  : '
$DC exec -T frontend sh -c 'wget -qO- -T 5 http://localhost:5173/api/reports 2>/dev/null | head -c 80' || printf 'BRAK ODPOWIEDZI'
echo

# ------------------------------------------------------------
echo; echo "=== F. FRONTEND — KOD (podejrzani od białego ekranu) ==="
echo "--- src/main.tsx ---"
sed 's/^/    /' meowhere_frontend/src/main.tsx 2>/dev/null

echo "--- App.tsx: importy, trasy, export ---"
grep -nE "^import|path=|path:|<Route|BrowserRouter|Routes|export default" meowhere_frontend/src/App.tsx 2>/dev/null | sed 's/^/    /'

if grep -qE 'path="/"|index' meowhere_frontend/src/App.tsx 2>/dev/null; then
  ok 'jest trasa "/" (lub index)'
else
  bad 'App.tsx nie ma trasy "/" — na stronie głównej nic się nie pokaże'
fi
if grep -qE 'export default' meowhere_frontend/src/App.tsx 2>/dev/null; then
  ok 'App.tsx ma export default (main.tsx importuje domyślnie)'
else
  bad 'App.tsx bez export default — import w main.tsx dostanie undefined'
fi

echo "--- api.ts: dokąd uderza ---"
grep -nE "localhost|127\.0\.0\.1|/api|BASE|const .*URL" meowhere_frontend/src/api.ts 2>/dev/null | head -25 | sed 's/^/    /'

echo "--- vite.config.ts: proxy ---"
grep -nE "target|API_TARGET|proxy|/api|/uploads|host|port" meowhere_frontend/vite.config.ts 2>/dev/null | sed 's/^/    /'

echo "--- process.env w kodzie przeglądarki (nie wolno!) ---"
if grep -rn "process\.env" meowhere_frontend/src >/dev/null 2>&1; then
  grep -rn "process\.env" meowhere_frontend/src | sed 's/^/    /'
  bad "process.env użyte w src/ — w przeglądarce to ReferenceError = biały ekran"
else
  ok "brak process.env w src/"
fi

echo "--- lokalne importy wskazujące na nieistniejące pliki ---"
FOUND=0
while IFS= read -r f; do
  dir=$(dirname "$f")
  while IFS= read -r imp; do
    [ -z "$imp" ] && continue
    t="$dir/$imp"
    if [ ! -e "$t" ] && [ ! -e "$t.tsx" ] && [ ! -e "$t.ts" ] && [ ! -e "$t.css" ] \
       && [ ! -e "$t/index.tsx" ] && [ ! -e "$t/index.ts" ]; then
      echo "    $f  ->  $imp"; FOUND=1
    fi
  done < <(grep -oE "from ['\"][.][^'\"]+" "$f" 2>/dev/null | sed -E "s/^from ['\"]//")
done < <(find meowhere_frontend/src -type f \( -name '*.tsx' -o -name '*.ts' \))
if [ "$FOUND" -eq 0 ]; then ok "wszystkie lokalne importy istnieją"; else problem "niektóre lokalne importy wskazują na brakujące pliki"; fi

# ------------------------------------------------------------
echo; echo "============================================================"
if [ -s "$PROBLEMS" ]; then
  echo "WERDYKT: znaleziono $(grep -c . "$PROBLEMS") problem(ów):"
  cat "$PROBLEMS"
else
  echo "WERDYKT: brak wykrytych problemów — struktura i połączenia OK."
fi
echo "============================================================"

rm -f "$PROBLEMS" /tmp/meowhere_cfg /tmp/meowhere_cfg_err
