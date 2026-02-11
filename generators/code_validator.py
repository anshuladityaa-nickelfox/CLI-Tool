"""
Code validator and fixer for AI-generated Python code
"""
import ast
import re


def fix_import_statements(code: str, app_name: str) -> str:
    """
    Fix import statements to use correct paths
    
    Args:
        code: Python code string
        app_name: Name of the app (e.g., 'uploads', 'mail_service')
        
    Returns:
        Fixed Python code with correct imports
    """
    lines = code.split('\n')
    fixed_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        # Fix: from app_name.module import X -> from .module import X (relative import)
        if stripped.startswith(f'from {app_name}.'):
            # Convert to relative import
            module = stripped.split(f'from {app_name}.')[1]
            line = line.replace(f'from {app_name}.', 'from .')
        
        # Fix: import app_name.module -> from . import module (if it's the same app)
        elif stripped.startswith(f'import {app_name}.'):
            module = stripped.split(f'import {app_name}.')[1].split()[0]
            line = line.replace(f'import {app_name}.{module}', f'from . import {module}')
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def fix_python_syntax(code: str, filename: str = "unknown", app_name: str = None) -> str:
    """
    Fix common Python syntax errors in AI-generated code
    
    Args:
        code: Python code string
        filename: Name of the file (for error messages)
        app_name: Name of the app (for fixing imports)
        
    Returns:
        Fixed Python code
    """
    original_code = code
    
    # Fix 0: Fix import statements if app_name is provided
    if app_name:
        code = fix_import_statements(code, app_name)
    
    # Fix 0.5: Fix common Django field parameter typos
    code = code.replace('auto_add_now=', 'auto_now_add=')
    code = code.replace('auto_now_add_now=', 'auto_now_add=')
    code = code.replace('autonow=', 'auto_now=')
    code = code.replace('blank_true=', 'blank=')
    code = code.replace('null_true=', 'null=')
    
    # Fix 1: Fix f-strings with nested quotes
    # Convert f"...{x.method('...')}..." to use escaped quotes or split the string
    def fix_fstring_quotes(match):
        content = match.group(1)
        # Replace double quotes inside with escaped quotes
        fixed_content = content.replace('"', '\\"')
        return f'f"{fixed_content}"'
    
    # Pattern to find f-strings with double quotes
    code = re.sub(r'f"([^"]*\{[^}]*\}[^"]*)"', fix_fstring_quotes, code)
    
    # Fix 2: Convert complex f-strings to simpler format
    lines = code.split('\n')
    fixed_lines = []
    
    for line in lines:
        # If line has f-string with strftime, split it
        if "f'" in line and 'strftime' in line and '(' in line:
            # Extract the strftime call and move it to a separate variable
            # This is a heuristic fix
            indent = len(line) - len(line.lstrip())
            indent_str = ' ' * indent
            
            # Simple fix: just use .format() instead
            if 'return f' in line:
                # Extract variable names from the f-string
                vars_in_fstring = re.findall(r'\{([^}]+)\}', line)
                if vars_in_fstring:
                    # Create a simpler version
                    line = line.replace("f'", "'").replace("f\"", "\"")
                    for var in vars_in_fstring:
                        if 'strftime' in var:
                            # Move strftime to separate line
                            var_name = var.split('.')[0]
                            date_var = f'{var_name}_str'
                            fixed_lines.append(f'{indent_str}{date_var} = {var}')
                            line = line.replace('{' + var + '}', '{' + date_var + '}')
        
        fixed_lines.append(line)
    
    code = '\n'.join(fixed_lines)
    
    # Fix 3: Remove any standalone dictionary keys (invalid syntax)
    lines = code.split('\n')
    fixed_lines = []
    for line in lines:
        stripped = line.strip()
        # Skip lines that look like dict keys without context
        if stripped.startswith("'") and "': " in stripped and not any(x in stripped for x in ['=', 'return', '{']):
            continue
        fixed_lines.append(line)
    
    code = '\n'.join(fixed_lines)
    
    # Fix 4: Validate the code
    try:
        ast.parse(code)
        return code
    except SyntaxError as e:
        # If still has errors, try to provide more specific fixes
        print(f"Warning: Syntax error in {filename} at line {e.lineno}: {e.msg}")
        
        # Try to fix the specific line
        lines = code.split('\n')
        if e.lineno and e.lineno <= len(lines):
            problem_line = lines[e.lineno - 1]
            
            # Common fixes
            if 'f"' in problem_line or "f'" in problem_line:
                # Remove f-string formatting
                lines[e.lineno - 1] = problem_line.replace('f"', '"').replace("f'", "'")
                code = '\n'.join(lines)
                
                # Try parsing again
                try:
                    ast.parse(code)
                    print(f"Fixed by removing f-string formatting")
                    return code
                except:
                    pass
        
        # If we can't fix it, return minimal valid code
        print(f"Returning minimal valid code for {filename}")
        return get_minimal_code(filename, app_name)
    except Exception as e:
        print(f"Warning: Unexpected error in {filename}: {str(e)}")
        return get_minimal_code(filename, app_name)


def get_minimal_code(filename: str, app_name: str = None) -> str:
    """Get minimal valid code for a given filename"""
    if filename == 'models.py':
        return """from django.db import models

# TODO: Add your models here

class ExampleModel(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
"""
    elif filename == 'views.py':
        return """from django.shortcuts import render
from rest_framework import viewsets

# TODO: Add your views here
"""
    elif filename == 'admin.py':
        return """from django.contrib import admin

# TODO: Register your models here
"""
    elif filename == 'urls.py':
        return """from django.urls import path

urlpatterns = [
    # TODO: Add your URL patterns here
]
"""
    elif filename == 'apps.py' and app_name:
        class_name = ''.join(word.capitalize() for word in app_name.split('_')) + 'Config'
        return f"""from django.apps import AppConfig

class {class_name}(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.{app_name}'
"""
    elif filename == 'apps.py':
        return """from django.apps import AppConfig

class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.app'
"""
    elif filename.endswith('.py'):
        return "# TODO: Add your code here\n"
    else:
        return ""


def validate_and_fix_files(files: dict, app_name: str = None) -> dict:
    """
    Validate and fix all Python files in the generated files dict
    
    Args:
        files: Dictionary of filename -> code
        app_name: Name of the app (for fixing imports)
        
    Returns:
        Dictionary of filename -> fixed code
    """
    fixed_files = {}
    
    for filename, code in files.items():
        if filename.endswith('.py'):
            try:
                # Apply general Python syntax fixes
                fixed_code = fix_python_syntax(code, filename, app_name)
                
                # Apply specific fixes based on filename and app
                if filename == 'models.py' and app_name == 'rbac':
                    fixed_code = fix_rbac_user_model(fixed_code)
                
                if filename == 'models.py':
                    fixed_code = fix_foreignkey_related_names(fixed_code)
                
                if filename == 'admin.py':
                    fixed_code = fix_duplicate_admin_registration(fixed_code)
                
                if filename == 'urls.py':
                    fixed_code = fix_duplicate_admin_urls(fixed_code)
                    fixed_code = ensure_urlpatterns(fixed_code)
                
                fixed_files[filename] = fixed_code
            except Exception as e:
                print(f"Error fixing {filename}: {str(e)}")
                fixed_files[filename] = get_minimal_code(filename, app_name)
        else:
            fixed_files[filename] = code
    
    return fixed_files


def fix_rbac_user_model(code: str) -> str:
    """
    Fix RBAC User model to avoid conflicts with Django's default User model
    
    Args:
        code: Python code string containing User model
        
    Returns:
        Fixed code with proper related_name attributes
    """
    # Check if this creates a custom User model extending AbstractUser
    if 'class User(AbstractUser)' not in code and 'class User(AbstractBaseUser)' not in code:
        return code
    
    print("Detected custom User model in RBAC - fixing to avoid conflicts...")
    
    # Add related_name to groups and user_permissions to avoid clashes
    if 'groups = models.ManyToManyField' not in code:
        # Add the fixed fields before the class Meta or at the end of the class
        lines = code.split('\n')
        fixed_lines = []
        user_class_found = False
        fields_added = False
        
        for i, line in enumerate(lines):
            fixed_lines.append(line)
            
            if 'class User(' in line:
                user_class_found = True
            
            # Add fields before Meta class or at the end of User class
            if user_class_found and not fields_added:
                if '    class Meta:' in line or (i + 1 < len(lines) and 'class ' in lines[i + 1] and not lines[i + 1].startswith('    ')):
                    # Insert before Meta or before next class
                    indent = '    '
                    fixed_lines.insert(-1, f"{indent}")
                    fixed_lines.insert(-1, f"{indent}# Fix clash with Django's default User model")
                    fixed_lines.insert(-1, f"{indent}groups = models.ManyToManyField(")
                    fixed_lines.insert(-1, f"{indent}    'auth.Group',")
                    fixed_lines.insert(-1, f"{indent}    verbose_name='groups',")
                    fixed_lines.insert(-1, f"{indent}    blank=True,")
                    fixed_lines.insert(-1, f"{indent}    related_name='rbac_user_set',")
                    fixed_lines.insert(-1, f"{indent}    related_query_name='rbac_user',")
                    fixed_lines.insert(-1, f"{indent})")
                    fixed_lines.insert(-1, f"{indent}user_permissions = models.ManyToManyField(")
                    fixed_lines.insert(-1, f"{indent}    'auth.Permission',")
                    fixed_lines.insert(-1, f"{indent}    verbose_name='user permissions',")
                    fixed_lines.insert(-1, f"{indent}    blank=True,")
                    fixed_lines.insert(-1, f"{indent}    related_name='rbac_user_set',")
                    fixed_lines.insert(-1, f"{indent}    related_query_name='rbac_user',")
                    fixed_lines.insert(-1, f"{indent})")
                    fields_added = True
        
        code = '\n'.join(fixed_lines)
    
    return code


def fix_duplicate_admin_urls(code: str) -> str:
    """
    Remove duplicate admin URLs from app urls.py files
    
    Args:
        code: Python code string containing URL patterns
        
    Returns:
        Fixed code without admin URLs (admin should only be in main urls.py)
    """
    # Check if this file has admin URLs
    if "path('admin/', admin.site.urls)" not in code:
        return code
    
    print("Removing duplicate admin URLs from app urls.py...")
    
    lines = code.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Skip lines with admin URLs
        if "path('admin/', admin.site.urls)" in line:
            continue
        # Remove admin import if it's not used elsewhere
        if line.strip() == 'from django.contrib import admin':
            # Check if admin is used elsewhere in the code
            if 'admin.site.urls' not in code.replace(line, ''):
                continue
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)


def fix_duplicate_admin_registration(code: str) -> str:
    """
    Fix duplicate admin registrations (both @admin.register and admin.site.register)
    
    Args:
        code: Python code string containing admin registrations
        
    Returns:
        Fixed code with only one registration method per model
    """
    # Find models registered with @admin.register decorator
    decorator_models = set()
    lines = code.split('\n')
    
    for i, line in enumerate(lines):
        if '@admin.register(' in line:
            # Extract model name from decorator
            match = re.search(r'@admin\.register\(([^)]+)\)', line)
            if match:
                models_str = match.group(1)
                # Handle multiple models in decorator
                models = [m.strip() for m in models_str.split(',')]
                decorator_models.update(models)
    
    # Remove admin.site.register() calls for models already registered with decorator
    if decorator_models:
        print(f"Removing duplicate admin.site.register() for models: {', '.join(decorator_models)}")
        fixed_lines = []
        
        for line in lines:
            # Check if this line is admin.site.register for a model already decorated
            if 'admin.site.register(' in line:
                skip = False
                for model in decorator_models:
                    if model in line:
                        skip = True
                        break
                if skip:
                    continue
            
            fixed_lines.append(line)
        
        code = '\n'.join(fixed_lines)
    
    return code


def ensure_urlpatterns(code: str) -> str:
    """
    Ensure urls.py has urlpatterns list
    
    Args:
        code: Python code string
        
    Returns:
        Fixed code with urlpatterns list
    """
    if 'urlpatterns' in code:
        return code
    
    print("Adding missing urlpatterns list to urls.py...")
    
    # Add urlpatterns at the end
    code = code.rstrip() + "\n\nurlpatterns = [\n    # Add your URL patterns here\n]\n"
    
    return code


def fix_foreignkey_related_names(code: str) -> str:
    """
    Add related_name to ForeignKey fields that might clash
    
    Args:
        code: Python code string containing models
        
    Returns:
        Fixed code with related_name attributes
    """
    # Common field names that clash with User model attributes
    clash_fields = ['email', 'username', 'groups', 'user_permissions']
    
    for field in clash_fields:
        # Look for ForeignKey without related_name
        pattern = f"{field} = models.ForeignKey(User, on_delete=models.CASCADE)"
        if pattern in code:
            print(f"Adding related_name to {field} ForeignKey to avoid clash...")
            replacement = f"{field} = models.ForeignKey(User, on_delete=models.CASCADE, related_name='{field}_set')"
            code = code.replace(pattern, replacement)
    
    # Also fix 'recipient' field which is common in email models
    pattern = "recipient = models.ForeignKey(User, on_delete=models.CASCADE)"
    if pattern in code:
        print("Adding related_name to recipient ForeignKey...")
        code = code.replace(pattern, "recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_emails')")
    
    return code


