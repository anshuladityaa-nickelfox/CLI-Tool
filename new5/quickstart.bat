@echo off
echo Quick starting new5...

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

if not exist venv\Lib\site-packages\django (
    echo Installing dependencies...
    pip install -r requirements.txt
)

if not exist .env (
    copy .env.example .env
)

if not exist db.sqlite3 (
    echo Running migrations...
    python manage.py migrate
)

echo Starting server...
python manage.py runserver
