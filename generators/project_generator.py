"""
Django Project Generator
Handles project structure creation and file generation
"""
import os
import ast
import time
from pathlib import Path
from typing import List, Dict
from rich.console import Console
# from generators.templates import (
#     get_manage_py, get_base_settings, get_base_urls,
#     get_env_template, get_dockerfile, get_docker_compose
# )  # Using AI generation instead
from generators.gitignore_template import get_gitignore
from generators.code_validator import validate_and_fix_files

console = Console()

class DjangoProjectGenerator:
    """Generates Django project with AI-powered features"""
    
    def __init__(self, project_name: str, features: List[str], ai_client):
        self.project_name = project_name
        self.features = features
        self.ai_client = ai_client
        self.project_path = Path(project_name)
        self.all_requirements = set(['Django>=4.2.0', 'djangorestframework>=3.14.0'])
        self.all_settings = []
        self.all_instructions = []
    
    def generate_project(self):
        """Generate complete Django project"""
        console.print(f"\n[cyan]Creating project directory: {self.project_name}[/cyan]")
        self._create_base_structure()
        
        console.print("[cyan]Generating Django base project...[/cyan]")
        self._create_django_base()
        
        for idx, feature in enumerate(self.features):
            console.print(f"[cyan]Generating feature: {feature}...[/cyan]")
            self._generate_feature(feature)
            
            # Add delay between feature requests to avoid rate limiting
            # Skip delay after the last feature
            if idx < len(self.features) - 1:
                delay = 3  # 3 seconds between features
                console.print(f"[dim]Waiting {delay} seconds before next feature...[/dim]")
                time.sleep(delay)
        
        console.print("[cyan]Creating requirements.txt...[/cyan]")
        self._create_requirements()
        
        console.print("[cyan]Creating setup scripts...[/cyan]")
        self._create_setup_scripts()
        
        console.print("[cyan]Creating documentation...[/cyan]")
        self._create_documentation()
        
        console.print("[cyan]Finalizing settings...[/cyan]")
        self._finalize_settings()
        
        console.print("[green]✓ Project generation complete![/green]")
    
    def _create_base_structure(self):
        """Create base project directory structure"""
        self.project_path.mkdir(exist_ok=True)
        (self.project_path / "apps").mkdir(exist_ok=True)
        (self.project_path / self.project_name).mkdir(exist_ok=True)
        (self.project_path / "templates").mkdir(exist_ok=True)
        (self.project_path / "static").mkdir(exist_ok=True)
        (self.project_path / "media").mkdir(exist_ok=True)
        
        # Create __init__.py for apps
        self._write_file("apps/__init__.py", "")
    
    def _create_django_base(self):
        """Create Django base configuration files using AI"""
        console.print("[cyan]Generating base Django files with AI...[/cyan]")
        
        # Generate manage.py
        manage_content = self.ai_client.generate_base_file('manage_py', self.project_name)
        self._write_file("manage.py", manage_content)
        
        # __init__.py files
        self._write_file(f"{self.project_name}/__init__.py", "")
        
        # Generate asgi.py
        asgi_content = self.ai_client.generate_base_file('asgi_py', self.project_name)
        self._write_file(f"{self.project_name}/asgi.py", asgi_content)
        
        # Generate wsgi.py
        wsgi_content = self.ai_client.generate_base_file('wsgi_py', self.project_name)
        self._write_file(f"{self.project_name}/wsgi.py", wsgi_content)
        
        # Generate settings.py
        settings_content = self.ai_client.generate_base_file('settings_py', self.project_name)
        self._write_file(f"{self.project_name}/settings.py", settings_content)
        
        # Generate urls.py
        urls_content = self.ai_client.generate_base_file('urls_py', self.project_name)
        self._write_file(f"{self.project_name}/urls.py", urls_content)
        
        # Generate .env.example
        env_content = self.ai_client.generate_base_file('env_example', self.project_name)
        self._write_file(".env.example", env_content)
        
        # .gitignore (keep template - it's just a list)
        self._write_file(".gitignore", get_gitignore())
        
        # Generate Dockerfile
        dockerfile_content = self.ai_client.generate_base_file('dockerfile', self.project_name)
        self._write_file("Dockerfile", dockerfile_content)
        
        # Generate docker-compose.yml
        compose_content = self.ai_client.generate_base_file('docker_compose', self.project_name)
        self._write_file("docker-compose.yml", compose_content)
    
    
    def _generate_feature(self, feature: str):
        """Generate code for a specific feature using AI"""
        try:
            context = {'project_name': self.project_name}
            result = self.ai_client.generate_django_code(feature, context)
            
            app_name = result.get('app_name', feature)
            files = result.get('files', {})
            settings = result.get('settings', '')
            requirements = result.get('requirements', [])
            instructions = result.get('instructions', '')
            
            # Validate and fix Python syntax errors
            console.print(f"[cyan]Validating generated code for {app_name}...[/cyan]")
            
            # Debug: Save raw files before validation
            import json
            debug_file = self.project_path / f"debug_{app_name}_raw.json"
            with open(debug_file, 'w') as f:
                json.dump(files, f, indent=2)
            
            files = validate_and_fix_files(files, app_name)
            
            # Fix apps.py to ensure correct name format
            if 'apps.py' in files:
                apps_content = files['apps.py']
                # Ensure the name field has 'apps.' prefix
                if f"name = '{app_name}'" in apps_content:
                    apps_content = apps_content.replace(
                        f"name = '{app_name}'",
                        f"name = 'apps.{app_name}'"
                    )
                    files['apps.py'] = apps_content
            
            # Create app directory
            app_path = self.project_path / "apps" / app_name
            app_path.mkdir(parents=True, exist_ok=True)
            
            # Create __init__.py
            self._write_file(f"apps/{app_name}/__init__.py", "")
            
            # Write all generated files
            for filename, content in files.items():
                self._write_file(f"apps/{app_name}/{filename}", content)
            
            # Ensure all required files exist
            required_files = ['models.py', 'admin.py', 'apps.py', 'urls.py', 'views.py']
            for req_file in required_files:
                file_path = self.project_path / "apps" / app_name / req_file
                if not file_path.exists():
                    console.print(f"[yellow]Creating missing {req_file} for {app_name}[/yellow]")
                    from generators.code_validator import get_minimal_code
                    minimal_content = get_minimal_code(req_file, app_name)
                    self._write_file(f"apps/{app_name}/{req_file}", minimal_content)
            
            # Collect requirements
            self.all_requirements.update(requirements)
            
            # Collect settings
            if settings:
                self.all_settings.append(f"\n# {app_name.upper()} Settings\n{settings}")
            
            # Collect instructions
            if instructions:
                self.all_instructions.append(f"\n## {app_name}\n{instructions}")
            
            # Update main settings.py
            self._update_settings(app_name)
            
            # Update main urls.py
            self._update_urls(app_name)
            
            console.print(f"[green]✓ Generated {app_name}[/green]")
            
        except Exception as e:
            console.print(f"[red]✗ Failed to generate {feature}: {str(e)}[/red]")
            console.print(f"[yellow]Skipping {feature}. You can try generating it again later.[/yellow]")
    
    def _update_settings(self, app_name: str):
        """Update settings.py to include new app"""
        settings_path = self.project_path / self.project_name / "settings.py"
        content = settings_path.read_text()
        
        # Add app to INSTALLED_APPS
        if f"'apps.{app_name}'" not in content:
            content = content.replace(
                "'rest_framework',",
                f"'rest_framework',\n    'apps.{app_name}',"
            )
        
        # If RBAC app, add AUTH_USER_MODEL setting
        if app_name == 'rbac' and 'AUTH_USER_MODEL' not in content:
            # Check if the RBAC models.py has a custom User model
            rbac_models_path = self.project_path / "apps" / "rbac" / "models.py"
            if rbac_models_path.exists():
                rbac_models = rbac_models_path.read_text()
                if 'class User(' in rbac_models and ('AbstractUser' in rbac_models or 'AbstractBaseUser' in rbac_models):
                    # Add AUTH_USER_MODEL after ALLOWED_HOSTS
                    content = content.replace(
                        "ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')",
                        "ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')\n\n# Custom User Model\nAUTH_USER_MODEL = 'rbac.User'"
                    )
                    console.print("[yellow]Added AUTH_USER_MODEL setting for custom RBAC User model[/yellow]")
        
        settings_path.write_text(content)
    
    def _update_urls(self, app_name: str):
        """Update urls.py to include new app URLs"""
        urls_path = self.project_path / self.project_name / "urls.py"
        content = urls_path.read_text()
        
        # Add URL pattern inside the urlpatterns list, before the closing bracket
        url_pattern = f"    path('api/{app_name}/', include('apps.{app_name}.urls')),"
        
        # Find the position to insert (before the closing bracket of urlpatterns)
        lines = content.split('\n')
        new_lines = []
        inserted = False
        
        for i, line in enumerate(lines):
            # Look for the comment marker or the closing bracket
            if '# Feature URLs will be added here' in line and not inserted:
                new_lines.append(line)
                new_lines.append(url_pattern)
                inserted = True
            elif not inserted and line.strip() == ']' and 'urlpatterns' in '\n'.join(lines[max(0, i-10):i]):
                # Insert before the closing bracket
                new_lines.append(url_pattern)
                new_lines.append(line)
                inserted = True
            else:
                new_lines.append(line)
        
        urls_path.write_text('\n'.join(new_lines))
    
    def _create_requirements(self):
        """Create requirements.txt file"""
        # Add essential packages
        self.all_requirements.update([
            'python-dotenv>=1.0.0',
            'gunicorn>=21.2.0',
            'psycopg2-binary>=2.9.9',
            'whitenoise>=6.6.0',
        ])
        
        requirements = sorted(self.all_requirements)
        content = "\n".join(requirements)
        self._write_file("requirements.txt", content)
    
    def _create_documentation(self):
        """Create setup documentation"""
        doc = f'''# {self.project_name}

AI-Generated Django Project with Advanced Features

## Features Included

{", ".join(self.features)}

## Setup Instructions

1. Create and activate virtual environment:
   ```bash
   python -m venv venv
   venv\\Scripts\\activate  # Windows
   source venv/bin/activate  # Unix/Mac
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   Create a `.env` file in the project root with necessary configurations.

4. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Run development server:
   ```bash
   python manage.py runserver
   ```

## Feature-Specific Setup

{"".join(self.all_instructions)}

## Additional Settings

Add the following to your settings.py if needed:

{"".join(self.all_settings)}

## Production Checklist

- [ ] Change SECRET_KEY in settings.py
- [ ] Set DEBUG = False
- [ ] Configure ALLOWED_HOSTS
- [ ] Set up proper database (PostgreSQL recommended)
- [ ] Configure email backend
- [ ] Set up static file serving
- [ ] Configure logging
- [ ] Set up SSL/TLS
- [ ] Configure CORS if needed
- [ ] Set up monitoring and error tracking

## API Documentation

Access the API at: http://localhost:8000/api/

Admin panel: http://localhost:8000/admin/

## Support

For issues or questions, refer to the Django documentation: https://docs.djangoproject.com/
'''
        self._write_file("SETUP.md", doc)
    
    def _write_file(self, relative_path: str, content: str):
        """Write content to file"""
        file_path = self.project_path / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding='utf-8')
    
    def _create_setup_scripts(self):
        """Create setup and run scripts for easy project initialization"""
        
        # Windows setup script
        setup_bat = f'''@echo off
echo ========================================
echo Setting up {self.project_name}
echo ========================================

echo.
echo Creating virtual environment...
python -m venv venv

echo.
echo Activating virtual environment...
call venv\\Scripts\\activate.bat

echo.
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Creating .env file...
if not exist .env (
    copy .env.example .env
    echo Please edit .env file with your configuration
)

echo.
echo Running migrations...
python manage.py makemigrations
python manage.py migrate

echo.
echo Creating superuser...
echo Please create an admin account:
python manage.py createsuperuser

echo.
echo Collecting static files...
python manage.py collectstatic --noinput

echo.
echo ========================================
echo Setup complete!
echo ========================================
echo.
echo To start the server, run: run.bat
pause
'''
        self._write_file("setup.bat", setup_bat)
        
        # Unix setup script
        setup_sh = f'''#!/bin/bash
echo "========================================"
echo "Setting up {self.project_name}"
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
'''
        self._write_file("setup.sh", setup_sh)
        
        # Windows run script
        run_bat = '''@echo off
call venv\\Scripts\\activate.bat
python manage.py runserver
'''
        self._write_file("run.bat", run_bat)
        
        # Unix run script
        run_sh = '''#!/bin/bash
source venv/bin/activate
python manage.py runserver
'''
        self._write_file("run.sh", run_sh)
        
        # Quick start script (no superuser creation)
        quickstart_bat = f'''@echo off
echo Quick starting {self.project_name}...

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\\Scripts\\activate.bat

if not exist venv\\Lib\\site-packages\\django (
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
'''
        self._write_file("quickstart.bat", quickstart_bat)
        
        # Unix quick start
        quickstart_sh = f'''#!/bin/bash
echo "Quick starting {self.project_name}..."

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
'''
        self._write_file("quickstart.sh", quickstart_sh)
    
    def _finalize_settings(self):
        """Add all collected settings to settings.py and clean up duplicates"""
        if not self.all_settings:
            return
        
        settings_path = self.project_path / self.project_name / "settings.py"
        content = settings_path.read_text()
        
        # Clean up the AI-generated settings to remove problematic code
        cleaned_settings = []
        for setting in self.all_settings:
            lines = setting.split('\n')
            valid_lines = []
            skip_block = False
            brace_count = 0
            
            for line in lines:
                stripped = line.strip()
                
                # Skip empty lines and keep comments
                if not stripped or stripped.startswith('#'):
                    valid_lines.append(line)
                    continue
                
                # Skip INSTALLED_APPS redefinitions
                if stripped.startswith('INSTALLED_APPS'):
                    skip_block = True
                    continue
                
                # Skip MIDDLEWARE redefinitions
                if stripped.startswith('MIDDLEWARE'):
                    skip_block = True
                    continue
                
                # Skip LOGGING redefinitions
                if stripped.startswith('LOGGING'):
                    skip_block = True
                    brace_count = 0
                    continue
                
                # Track braces for skipping blocks
                if skip_block:
                    if '{' in line:
                        brace_count += line.count('{')
                    if '}' in line:
                        brace_count -= line.count('}')
                    if '[' in line and brace_count == 0:
                        # Track brackets too
                        pass
                    if ']' in line and brace_count == 0:
                        skip_block = False
                    if brace_count == 0 and ']' in line:
                        skip_block = False
                    continue
                
                # Only keep valid Python assignment statements
                # Must have '=' and not be a dict key
                if '=' in stripped and not stripped.startswith("'") and not stripped.startswith('"'):
                    # This looks like a valid setting
                    valid_lines.append(line)
                elif stripped.startswith('import ') or stripped.startswith('from '):
                    # Keep imports
                    valid_lines.append(line)
            
            # Only add if we have valid content
            cleaned_content = '\n'.join(valid_lines).strip()
            if cleaned_content and not cleaned_content.startswith('#'):
                cleaned_settings.append(cleaned_content)
        
        # Add all cleaned feature settings
        if cleaned_settings:
            settings_additions = "\n\n".join(cleaned_settings)
            content += f"\n\n{settings_additions}\n"
        
        # Validate the final settings file
        settings_path.write_text(content)
        
        # Try to parse it to ensure it's valid Python
        try:
            import ast
            ast.parse(content)
            console.print("[green]✓ Settings file validated successfully[/green]")
        except SyntaxError as e:
            console.print(f"[yellow]⚠ Warning: Settings file has syntax error at line {e.lineno}[/yellow]")
            console.print(f"[yellow]  Error: {e.msg}[/yellow]")
            console.print(f"[yellow]  You may need to manually fix the settings.py file[/yellow]")
