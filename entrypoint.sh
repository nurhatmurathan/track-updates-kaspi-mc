#!/bin/bash
set -e

# Applying migrations
echo "👉 Applying migrations..."
alembic -c src/alembic.ini upgrade head

# Start
echo "🚀 Start Process ..."
python src/process_loop.py
