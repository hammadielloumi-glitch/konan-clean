#!/bin/bash
set -e

echo "=== Installation de pgvector (v0.8.1) ==="

# donner temporairement les droits root à apt
chmod 1777 /var/lib/apt/lists || true
mkdir -p /var/lib/apt/lists/partial || true

apt-get update -o Dir::Etc::sourcelist="sources.list" -o Dir::Etc::sourceparts="-" -o APT::Get::List-Cleanup="0"
apt-get install -y git build-essential postgresql-server-dev-16

cd /tmp
git clone --branch v0.8.1 https://github.com/pgvector/pgvector.git
cd pgvector
make
make install

echo "✅ Extension pgvector installée avec succès"
