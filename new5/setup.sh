#!/bin/bash
echo "========================================"
echo "Setting up new5"
echo "========================================"

echo ""
echo "Creating virtual environment..."
python3 -m venv venv

echo ""
echo "Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Creating .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Please edit .env file with your configuration"
fi

echo ""
echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

echo ""
echo "Creating superuser..."
echo "Please create an admin account:"
python manage.py createsuperuser

echo ""
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "========================================"
echo "Setup complete!"
echo "========================================"
echo ""
echo "To start the server, run: ./run.sh"
