# Django Project Generator (Nickelfox)

AI-powered Django project scaffolder using Groq's Llama 3.3 model. Generate production-ready Django projects with advanced features in seconds.

## Features

- 🤖 **AI-Powered Code Generation** - Uses Llama 3.3 70B for intelligent code generation
- 🚀 **Instant Setup** - Automated venv, dependencies, migrations, and superuser creation
- 📁 **Organized Structure** - Separate folders for DB services (apps/) and utilities (common/)
- 🌍 **Multi-Environment** - Pre-configured dev, staging, and production settings
- 🔧 **6 Advanced Features** - Mail, Notifications, RBAC, Uploads, Error Handling, Logging
- ✅ **Auto-Validation** - Built-in code validator fixes common Django errors
- 🐳 **Docker Ready** - Includes Dockerfile and docker-compose.yml
- 🎯 **Production Ready** - PostgreSQL, security hardening, and logging configured

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd "CLI tool 2"

# Install globally
pip install -e .
```

### Configuration

```bash
# Create config directory
mkdir ~/.nfxinit

# Copy template
cp .env.example ~/.nfxinit/.env

# Edit and add your API key
# Windows: notepad ~/.nfxinit/.env
# Linux/Mac: nano ~/.nfxinit/.env
```

Add your Groq API key to `~/.nfxinit/.env`:
```
GROQ_API_KEY=your_groq_api_key_here
```

Get your free API key from: https://console.groq.com/keys

### Usage

```bash
# Run from anywhere
NFXinit

# Or explicitly
NFXinit create-project

# Show version
NFXinit version

# Show help
NFXinit --help
```

## Project Generation Flow

1. **Enter project name** (e.g., "myproject")
2. **Choose directory** (default: parent folder of NFXinit)
3. **Select features** (1-6 or 'all')
4. **Confirm** and wait for generation
5. **Automatic setup**:
   - Creates virtual environment
   - Installs dependencies
   - Runs migrations
   - Creates superuser (username: `{project_name}.com`, password: `admin123`)
6. **Optional**: Start development server immediately

## Generated Project Structure

```
myproject/
├── config/                      # Django configuration
│   ├── settings/
│   │   ├── __init__.py         # Auto-loads based on DJANGO_ENV
│   │   ├── base.py             # Common settings
│   │   ├── development.py      # Dev (SQLite)
│   │   ├── staging.py          # Staging (PostgreSQL)
│   │   └── production.py       # Production (PostgreSQL + Security)
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/                        # DB-based services
│   ├── mail_service/
│   ├── notifications/
│   ├── rbac/
│   ├── uploads/
│   └── logging_system/
├── common/                      # Non-DB utilities
│   └── error_handler/
├── templates/
├── static/
├── media/
├── logs/
├── venv/                        # Virtual environment
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## Available Features

1. **Mail Services** - Email sending with templates and tracking
2. **Notification System** - User notifications (in-app, email, push)
3. **RBAC** - Role-Based Access Control with permissions
4. **Upload Documents** - File upload handling with validation
5. **Global Error Handling** - Centralized error logging and tracking
6. **Logging System** - Multi-level logging (console, file, database)

## Environment Configuration

### Development (Default)
```bash
# Uses SQLite, DEBUG=True
python manage.py runserver
```

### Staging
```bash
# Uses PostgreSQL
DJANGO_ENV=staging python manage.py runserver
```

### Production
```bash
# Uses PostgreSQL with security hardening
DJANGO_ENV=production gunicorn config.wsgi:application
```

### Environment Variables

Create a `.env` file in your project root:

```env
# Environment: dev, staging, production
DJANGO_ENV=dev

# Django
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL (for staging/production)
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@example.com

# AWS S3 (optional)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_REGION_NAME=us-east-1

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# Celery (optional)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## Commands

```bash
# Generate project
NFXinit
NFXinit create-project

# Show version
NFXinit version

# Show help
NFXinit --help

# Verify setup
python verify_setup.py
```

## Default Credentials

After project generation:
- **Admin URL**: http://127.0.0.1:8000/admin/
- **Username**: `{project_name}.com` (e.g., myproject.com)
- **Password**: `admin123`

⚠️ **Change these credentials in production!**

## Troubleshooting

### API Key Not Found
```bash
# Check if config exists
ls ~/.nfxinit/.env

# If not, create it
mkdir -p ~/.nfxinit
cp .env.example ~/.nfxinit/.env
# Edit and add your GROQ_API_KEY
```

### Command Not Found
If `NFXinit` is not found after installation:

1. **Check if pip bin directory is in PATH:**
   ```bash
   # Windows
   echo %PATH%
   
   # Unix/Mac
   echo $PATH
   ```

2. **Add to PATH if needed:**
   ```bash
   # Windows (PowerShell)
   $env:Path += ";C:\Users\YourUsername\AppData\Local\Programs\Python\Python311\Scripts"
   
   # Unix/Mac
   export PATH="$HOME/.local/bin:$PATH"
   ```

3. **Reinstall:**
   ```bash
   pip uninstall django-nfxinit -y
   pip install -e .
   ```

### Migration Errors
If migrations fail, run manually:
```bash
cd your_project
venv\Scripts\activate  # Windows
source venv/bin/activate  # Unix/Mac
python manage.py makemigrations
python manage.py migrate
```

## Technology Stack

- **Python**: 3.8+
- **Django**: 4.2+
- **Django REST Framework**: 3.14+
- **AI Model**: Llama 3.3 70B (via Groq)
- **Database**: SQLite (dev), PostgreSQL (staging/prod)
- **CLI**: Typer + Rich

## Features in Detail

### Mail Service
- Send emails with templates
- Track email status
- Queue management
- Attachment support

### Notifications
- Multiple channels (in-app, email, push)
- User preferences
- Read/unread status
- Notification history

### RBAC (Role-Based Access Control)
- Custom roles and permissions
- User-role assignments
- Permission checking decorators
- Admin interface for management

### File Uploads
- Secure file handling
- File type validation
- Size limits
- Storage management (local/S3)

### Error Handling
- Global exception handling
- Error logging
- User-friendly error pages
- Admin error dashboard

### Logging System
- Multi-level logging (DEBUG, INFO, WARNING, ERROR)
- Console and file handlers
- Rotating log files
- Database logging option

## Development

### Project Structure
```
CLI tool 2/
├── generators/
│   ├── ai_client.py           # Groq API integration
│   ├── project_generator.py   # Project scaffolding
│   ├── code_validator.py      # Syntax validation
│   ├── templates.py           # Base templates
│   └── gitignore_template.py  # .gitignore template
├── main.py                     # CLI entry point
├── prompts.json               # AI prompts
├── setup.py                   # Package config
├── requirements.txt           # Dependencies
└── README.md
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

Copyright © 2024 Nickelfox. All rights reserved.

## Support

For issues or questions:
- Email: info@nickelfox.com
- Website: https://nickelfox.com

## Changelog

### v1.0.0 (Current)
- ✅ AI-powered code generation with Llama 3.3
- ✅ Automated project setup (venv, deps, migrations)
- ✅ Multi-environment configuration (dev/staging/prod)
- ✅ Organized folder structure (apps/common)
- ✅ 6 advanced features
- ✅ Auto-validation and error fixing
- ✅ Docker support
- ✅ PostgreSQL for staging/production
- ✅ Security hardening for production

---

**Made with ❤️ by Nickelfox**
