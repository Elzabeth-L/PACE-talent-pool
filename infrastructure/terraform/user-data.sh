#!/usr/bin/env bash
set -euo pipefail

apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y docker.io docker-compose-v2 unzip curl openssl
systemctl enable --now docker
mkdir -p /opt/pace-talent-pool
DB_PASSWORD="$(openssl rand -hex 24)"
cat > /opt/pace-talent-pool/.env <<EOF
POSTGRES_DB=pace_talent_pool
POSTGRES_USER=pace
POSTGRES_PASSWORD=${DB_PASSWORD}
DATABASE_URL=postgresql+psycopg://pace:${DB_PASSWORD}@db:5432/pace_talent_pool
EOF
chmod 600 /opt/pace-talent-pool/.env
