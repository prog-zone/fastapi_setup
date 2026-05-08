#!/bin/bash
set -e

# 1. Pull metadata from the static pyproject.toml
PROJECT_NAME=$(python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['name'])")
TOML_VERSION=$(python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")

# 2. Pull currently running version from Docker
RUNNING_VERSION=$(docker ps --filter "name=${PROJECT_NAME}_api" --format "{{.Image}}" | cut -d':' -f2)

# 3. Decision Logic (Handled in Python for safe SemVer comparison)
# Returns TOML_VERSION if higher, otherwise increments the RUNNING_VERSION minor
VERSION=$(python3 -c "
import sys

v_toml = '$TOML_VERSION'
v_run = '$RUNNING_VERSION'

if not v_run or v_run == 'latest':
    print(v_toml)
    sys.exit(0)

def parse_v(v): return [int(x) for x in v.split('.')]

try:
    if parse_v(v_toml) > parse_v(v_run):
        print(v_toml)
    else:
        parts = parse_v(v_run)
        parts[-1] += 1
        print('.'.join(map(str, parts)))
except:
    print(v_toml)
")

echo "🚀 Determined Version: $VERSION (TOML: $TOML_VERSION | Running: ${RUNNING_VERSION:-None})"

# 4. Load Secrets (Environment only)
set -a
[ -f .env ] && source .env
set +a

# 5. Export for Docker Compose
export PROJECT_NAME=$PROJECT_NAME
export APP_VERSION=$VERSION

# 6. Database Backup
if docker ps --format '{{.Names}}' | grep -q "${PROJECT_NAME}_db"; then
    docker exec ${PROJECT_NAME}_db pg_dump -U ${POSTGRES_USER} ${POSTGRES_DB} > "pre_${VERSION}.sql"
fi

# 7. Build and Deploy
docker compose build
docker compose up -d

echo "✅ Successfully deployed $PROJECT_NAME:$VERSION"