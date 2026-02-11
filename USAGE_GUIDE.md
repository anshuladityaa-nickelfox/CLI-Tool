# Complete Usage Guide

## Quick Start (5 Minutes)

### Step 1: Setup the Scaffolder

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env

# Add your Gemini API key to .env
# GEMINI_API_KEY=your_key_here
```

### Step 2: Generate Your Project

```bash
python main.py create-project
```

Answer the prompts:
- **Project name**: `my_blog` (or any name you want)
- **Language**: `1` (Python/Django)
- **Features**: `all` (or specific numbers like `1,2,3`)

### Step 3: Run Your Project

```bash
cd my_blog
quickstart.bat    # Windows
# OR
./quickstart.sh   # Linux/Mac
```

That's it! Your Django project is now running at http://localhost:8000/

## Detailed Walkthrough

### Understanding the Generated Project

When you generate a project with all features, you get:

```
my_blog/
├── manage.py                    # Django CLI
├── requirements.txt             # Dependencies
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
├── setup.bat / setup.sh         # Full setup (creates superuser)
├── quickstart.bat / quickstart.sh  # Quick start (no superuser)
├── run.bat / run.sh             # Just run the server
├── Dockerfile                   # Docker configuration
├── docker-compose.yml           # Docker Compose
├── SETUP.md                     # Detailed documentation
├── my_blog/                     # Main project
│   ├── settings.py              # All configurations
│   ├── urls.py                  # URL routing
│   ├── wsgi.py & asgi.py        # Server interfaces
├── apps/                        # Feature apps
│   ├── mail_service/            # Email functionality
│   ├── notifications/           # Notifications
│   ├── rbac/                    # Access control
│   ├── uploads/                 # File uploads
│   ├── error_handler/           # Error handling
│   └── logging_system/          # Logging
├── templates/                   # HTML templates
├── static/                      # CSS, JS, images
├── media/                       # User uploads
└── logs/                        # Application logs
```

### Setup Scripts Explained

#### setup.bat / setup.sh (Full Setup)
- Creates virtual environment
- Installs all dependencies
- Creates .env file
- Runs database migrations
- **Prompts you to create a superuser**
- Collects static files

Use this for the first time setup when you want full admin access.

#### quickstart.bat / quickstart.sh (Quick Start)
- Creates virtual environment (if needed)
- Installs dependencies (if needed)
- Creates .env file (if needed)
- Runs migrations (if needed)
- **Starts server immediately** (no superuser prompt)

Use this when you want to quickly test the project without admin access.

#### run.bat / run.sh (Just Run)
- Activates virtual environment
- Starts the development server

Use this after initial setup when you just want to run the server.

### Manual Setup (If You Prefer)

```bash
# 1. Navigate to project
cd my_blog

# 2. Create virtual environment
python -m venv venv

# 3. Activate it
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/Mac

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create .env file
copy .env.example .env     # Windows
cp .env.example .env       # Linux/Mac

# 6. Run migrations
python manage.py makemigrations
python manage.py migrate

# 7. Create superuser (optional)
python manage.py createsuperuser

# 8. Collect static files
python manage.py collectstatic --noinput

# 9. Run server
python manage.py runserver
```

### Accessing Your Application

Once the server is running:

1. **Homepage**: http://localhost:8000/
2. **Admin Panel**: http://localhost:8000/admin/
   - Login with the superuser credentials you created
3. **API Root**: http://localhost:8000/api/
4. **REST Framework**: http://localhost:8000/api/auth/

### Feature-Specific URLs

Each feature has its own API endpoints:

- **Mail Service**: http://localhost:8000/api/mail_service/
- **Notifications**: http://localhost:8000/api/notifications/
- **RBAC**: http://localhost:8000/api/rbac/
- **Uploads**: http://localhost:8000/api/uploads/
- **Error Handler**: http://localhost:8000/api/error_handler/
- **Logging**: http://localhost:8000/api/logging_system/

### Configuration

#### Environment Variables (.env)

The `.env` file controls your project configuration:

```env
# Basic Settings
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email (for mail service feature)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

#### Database

By default, projects use SQLite (no setup needed). For production, use PostgreSQL:

1. Install PostgreSQL
2. Create a database
3. Update `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'my_blog_db',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Docker Deployment

Every project includes Docker configuration:

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access at http://localhost:8000/
```

### Common Tasks

#### Create a New App

```bash
python manage.py startapp my_new_app apps/my_new_app
```

Then add `'apps.my_new_app'` to `INSTALLED_APPS` in `settings.py`.

#### Make Database Changes

```bash
# After modifying models.py
python manage.py makemigrations
python manage.py migrate
```

#### Create Superuser

```bash
python manage.py createsuperuser
```

#### Collect Static Files

```bash
python manage.py collectstatic
```

#### Run Tests

```bash
python manage.py test
```

### Troubleshooting

#### "Module not found" errors
```bash
# Make sure virtual environment is activated
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/Mac

# Reinstall dependencies
pip install -r requirements.txt
```

#### "No such table" errors
```bash
# Run migrations
python manage.py migrate
```

#### "Port already in use"
```bash
# Use a different port
python manage.py runserver 8001
```

#### Static files not loading
```bash
# Collect static files
python manage.py collectstatic --noinput
```

### Production Deployment

Before deploying to production:

1. **Security**:
   - Change `SECRET_KEY` in `.env`
   - Set `DEBUG=False`
   - Configure `ALLOWED_HOSTS`

2. **Database**:
   - Use PostgreSQL instead of SQLite
   - Set up database backups

3. **Static Files**:
   - Run `collectstatic`
   - Use WhiteNoise (already configured) or CDN

4. **Email**:
   - Configure real SMTP settings
   - Test email sending

5. **Monitoring**:
   - Set up Sentry for error tracking
   - Configure logging

6. **Server**:
   - Use Gunicorn (included in requirements)
   - Set up Nginx as reverse proxy
   - Configure SSL/TLS

### Next Steps

1. **Customize**: Modify the generated code to fit your needs
2. **Add Models**: Create your data models in `apps/*/models.py`
3. **Create Views**: Add your business logic in `apps/*/views.py`
4. **Design Templates**: Create HTML templates in `templates/`
5. **Add Tests**: Write tests in `apps/*/tests.py`
6. **Deploy**: Follow the production checklist above

### Getting Help

- Check `SETUP.md` in your generated project
- Review Django docs: https://docs.djangoproject.com/
- Check feature-specific documentation in each app

### Tips

- Use `quickstart` for rapid testing
- Use `setup` for full development environment
- Always activate virtual environment before running commands
- Keep `.env` file secure (never commit to git)
- Run migrations after pulling code changes
- Use Django admin for quick data management

## Example: Creating a Blog

```bash
# 1. Generate project
python main.py create-project
# Name: my_blog
# Features: 1,4,5,6 (Mail, Upload, Error Handling, Logging)

# 2. Quick start
cd my_blog
quickstart.bat

# 3. Create blog app
python manage.py startapp blog apps/blog

# 4. Add to INSTALLED_APPS in settings.py
# 'apps.blog',

# 5. Create models in apps/blog/models.py
# 6. Make migrations
python manage.py makemigrations
python manage.py migrate

# 7. Create superuser
python manage.py createsuperuser

# 8. Run server
python manage.py runserver

# 9. Access admin at http://localhost:8000/admin/
```

That's it! You now have a fully functional Django blog with mail services, file uploads, error handling, and logging!
