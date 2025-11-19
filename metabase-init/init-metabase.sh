#!/usr/bin/env bash
set -euo pipefail

echo "[INIT] Starting Metabase init script..."

########################################
# Environment defaults (safe, overridable)
########################################
MB_HOST="${MB_HOST:-metabase}"
MB_PORT="${MB_PORT:-3000}"
MB_SITE_NAME="${MB_SITE_NAME:-CHAI Weather Analytics}"

MB_ADMIN_EMAIL="${MB_ADMIN_EMAIL:-chai.admin@example.com}"
MB_ADMIN_PASSWORD="${MB_ADMIN_PASSWORD:-ChaiAdmin#2025}"
MB_ADMIN_FIRST_NAME="${MB_ADMIN_FIRST_NAME:-Chai}"
MB_ADMIN_LAST_NAME="${MB_ADMIN_LAST_NAME:-Admin}"

DB_HOST="${DB_HOST:-chai_postgres}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-chaidb}"
DB_USER="${DB_USER:-chai}"
DB_PASS="${DB_PASS:-chai123}"

BASE_URL="http://${MB_HOST}:${MB_PORT}"

echo "[INIT] Metabase host: ${BASE_URL}"
echo "[INIT] Target DB: ${DB_USER}@${DB_HOST}:${DB_PORT}/${DB_NAME}"

########################################
# 1. Wait for Metabase to become healthy
########################################
echo "[INIT] Waiting for Metabase health..."

for i in {1..60}; do
  if curl -s "${BASE_URL}/api/health" | grep -q '"ok"'; then
    echo "[INIT] Metabase is healthy."
    break
  fi
  echo "[INIT] ... still waiting (${i})"
  sleep 5
done

# One last check
if ! curl -s "${BASE_URL}/api/health" | grep -q '"ok"'; then
  echo "[INIT] ERROR: Metabase never became healthy."
  exit 1
fi

########################################
# 2. Get setup token – if empty, already configured
########################################
echo "[INIT] Checking setup token..."
PROPS_JSON=$(curl -s "${BASE_URL}/api/session/properties" || true)
SETUP_TOKEN=$(echo "${PROPS_JSON}" | sed -n 's/.*"setup-token":"\([^"]*\)".*/\1/p')

if [[ -z "${SETUP_TOKEN}" ]]; then
  echo "[INIT] No setup token found – Metabase is already configured. Skipping setup."
else
  echo "[INIT] Got setup token: ${SETUP_TOKEN}"
  echo "[INIT] Running automated Metabase setup..."

  SETUP_PAYLOAD=$(cat <<EOF
{
  "token": "${SETUP_TOKEN}",
  "user": {
    "first_name": "${MB_ADMIN_FIRST_NAME}",
    "last_name": "${MB_ADMIN_LAST_NAME}",
    "email": "${MB_ADMIN_EMAIL}",
    "password": "${MB_ADMIN_PASSWORD}"
  },
  "prefs": {
    "site_name": "${MB_SITE_NAME}",
    "site_locale": "en",
    "report_time": "09:00",
    "report_day": "mon"
  }
}
EOF
)

  # We capture both body and status code
  RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${BASE_URL}/api/setup" \
    -H "Content-Type: application/json" \
    -d "${SETUP_PAYLOAD}")

  HTTP_BODY=$(echo "${RESPONSE}" | sed '$d')
  HTTP_CODE=$(echo "${RESPONSE}" | tail -n1)

  if [[ "${HTTP_CODE}" != "200" && "${HTTP_CODE}" != "201" ]]; then
    echo "[INIT] ERROR: /api/setup returned HTTP ${HTTP_CODE}"
    echo "[INIT] Response body: ${HTTP_BODY}"
    exit 1
  fi

  echo "[INIT] Metabase setup complete."
fi

########################################
# 3. Log in to Metabase (get session token)
########################################
echo "[INIT] Logging in as admin to obtain session..."

LOGIN_PAYLOAD=$(cat <<EOF
{
  "username": "${MB_ADMIN_EMAIL}",
  "password": "${MB_ADMIN_PASSWORD}"
}
EOF
)

LOGIN_HEADERS=$(curl -i -s -X POST "${BASE_URL}/api/session" \
  -H "Content-Type: application/json" \
  -d "${LOGIN_PAYLOAD}" || true)

SESSION_ID=$(echo "${LOGIN_HEADERS}" | sed -n 's/^Set-Cookie: metabase.SESSION=\([^;]*\);.*/\1/p')

if [[ -z "${SESSION_ID}" ]]; then
  echo "[INIT] ERROR: Could not obtain Metabase session cookie."
  echo "[INIT] Raw login headers:"
  echo "${LOGIN_HEADERS}"
  exit 1
fi

echo "[INIT] Got Metabase session."

########################################
# 4. Ensure CHAI Weather Warehouse DB exists
########################################
echo "[INIT] Checking if CHAI Weather Warehouse database already exists..."

EXISTING_DBS=$(curl -s -H "X-Metabase-Session: ${SESSION_ID}" "${BASE_URL}/api/database")
HAS_CHAI_DB=$(echo "${EXISTING_DBS}" | grep -c '"name":"CHAI Weather Warehouse"' || true)

if [[ "${HAS_CHAI_DB}" -gt 0 ]]; then
  echo "[INIT] CHAI Weather Warehouse already configured. Nothing to do."
  echo "[INIT] Metabase init done."
  exit 0
fi

echo "[INIT] Creating CHAI Weather Warehouse database connection..."

DB_PAYLOAD=$(cat <<EOF
{
  "name": "CHAI Weather Warehouse",
  "engine": "postgres",
  "details": {
    "host": "${DB_HOST}",
    "port": ${DB_PORT},
    "dbname": "${DB_NAME}",
    "user": "${DB_USER}",
    "password": "${DB_PASS}",
    "ssl": false
  },
  "is_full_sync": true,
  "is_on_demand": false,
  "schedules": {}
}
EOF
)

DB_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${BASE_URL}/api/database" \
  -H "Content-Type: application/json" \
  -H "X-Metabase-Session: ${SESSION_ID}" \
  -d "${DB_PAYLOAD}")

DB_BODY=$(echo "${DB_RESPONSE}" | sed '$d')
DB_CODE=$(echo "${DB_RESPONSE}" | tail -n1)

if [[ "${DB_CODE}" != "200" && "${DB_CODE}" != "201" ]]; then
  echo "[INIT] ERROR: /api/database returned HTTP ${DB_CODE}"
  echo "[INIT] Response body: ${DB_BODY}"
  exit 1
fi

echo "[INIT] CHAI Weather Warehouse database created successfully."
echo "[INIT] Metabase init completed successfully."
