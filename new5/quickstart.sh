#!/bin/bash
echo "Quick starting new5..."

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

if [ ! -d "venv/lib/python*/site-packages/django" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

if [ ! -f ".env" ]; then
    cp .env.example .env
fi

if [ ! -f "db.sqlite3" ]; then
    echo "Running migrations..."
    python manage.py migrate
fi

echo "Starting server..."
python manage.py runserver
