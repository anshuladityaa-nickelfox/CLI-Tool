"""
AI Client for code generation using Groq
"""
import requests
from typing import Dict, List
import json
import re
import time
from pathlib import Path


class AIClient:
    """Client for interacting with Groq API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        # Use llama3 - better at following instructions than qwen
        self.model = "llama-3.3-70b-versatile"
        
        # Load prompts from JSON file
        prompts_file = Path(__file__).parent.parent / 'prompts.json'
        with open(prompts_file, 'r') as f:
            self.prompts_config = json.load(f)
    
    def generate_django_code(self, feature: str, context: Dict) -> Dict:
        """
        Generate Django code for a specific feature using AI
        
        Args:
            feature: Feature name (mail, notification, rbac, etc.)
            context: Additional context for code generation
            
        Returns:
            Dictionary containing generated files and their content
        """
        print(f"[INFO] Generating {feature} using AI (llama-3.3)...")
        
        # Use batch generation (file by file) - NO FALLBACK
        return self._generate_in_batches(feature, context)
    
    def _generate_in_batches(self, feature: str, context: Dict) -> Dict:
        """
        Generate files one by one to avoid large responses
        
        Args:
            feature: Feature name
            context: Generation context
            
        Returns:
            Combined result dictionary
        """
        project_name = context.get('project_name', 'myproject')
        
        # Get feature configuration
        features = self.prompts_config.get('features', {})
        feature_config = features.get(feature, {
            "app_name": feature,
            "description": feature
        })
        
        app_name = feature_config.get('app_name', feature)
        feature_desc = feature_config.get('description', feature)
        
        # Files to generate
        files_to_generate = ['models.py', 'admin.py', 'views.py', 'urls.py', 'apps.py']
        
        generated_files = {}
        
        # Generate each file separately
        for filename in files_to_generate:
            try:
                print(f"  Generating {filename}...")
                file_content = self._generate_single_file(
                    app_name=app_name,
                    feature_desc=feature_desc,
                    filename=filename,
                    project_name=project_name,
                    existing_files=generated_files  # Pass existing files for context
                )
                generated_files[filename] = file_content
                print(f"  ✓ {filename}")
                
                # Small delay between files
                time.sleep(0.5)
                
            except Exception as e:
                print(f"  ✗ {filename} failed: {str(e)}")
                # Use minimal code for failed file
                from generators.code_validator import get_minimal_code
                generated_files[filename] = get_minimal_code(filename, app_name)
        
        # Fix import mismatches between files
        generated_files = self._fix_import_mismatches(generated_files, app_name)
        
        print(f"[SUCCESS] Generated {app_name}")
        
        # Return in expected format
        return {
            "app_name": app_name,
            "files": generated_files,
            "settings": "",
            "requirements": [],
            "instructions": f"{app_name} generated"
        }
    
    def _generate_single_file(self, app_name: str, feature_desc: str, filename: str, project_name: str, existing_files: dict = None) -> str:
        """Generate a single file using AI"""
        prompt = self._build_single_file_prompt(app_name, feature_desc, filename, existing_files)
        
        max_retries = 2
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    time.sleep(2)
                
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a Python code generator. You ONLY output valid Python code. Never add explanations, comments, or markdown. Just pure Python code that can be executed directly."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.0,  # Zero temperature for deterministic output
                    "max_tokens": 500,
                    "top_p": 1.0
                }
                
                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 429:
                    if attempt < max_retries - 1:
                        continue
                    raise Exception("Rate limit")
                
                response.raise_for_status()
                result = response.json()
                
                if 'choices' in result and len(result['choices']) > 0:
                    code = result['choices'][0]['message']['content'].strip()
                    
                    # Save raw response for debugging
                    if not code:
                        print(f"    Empty response from API")
                        raise Exception("Empty")
                    
                    # Clean markdown
                    if code.startswith("```python"):
                        code = code[9:]
                    elif code.startswith("```"):
                        code = code[3:]
                    if code.endswith("```"):
                        code = code[:-3]
                    
                    code = code.strip()
                    
                    # Remove any explanatory text before or after code
                    lines = code.split('\n')
                    code_lines = []
                    in_code = False
                    
                    for line in lines:
                        stripped = line.strip()
                        # Start collecting when we see imports or class/def
                        if stripped.startswith(('from ', 'import ', 'class ', 'def ', '@')):
                            in_code = True
                        
                        if in_code:
                            code_lines.append(line)
                    
                    if code_lines:
                        code = '\n'.join(code_lines)
                    
                    # Basic validation - check for unterminated strings
                    try:
                        compile(code, '<string>', 'exec')
                        print(f"    ✓ Valid Python")
                    except SyntaxError as e:
                        print(f"    ✗ Syntax error: {e}")
                        # Don't try to fix, just fail and retry
                        raise Exception(f"Invalid Python: {e}")
                    
                    if not code:
                        raise Exception("Empty")
                    
                    return code
                else:
                    raise Exception("Invalid response")
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"    Retry {attempt + 2}...")
                    continue
                # Save failed response for debugging
                print(f"    Failed: {str(e)}")
                raise e
    
    def _build_single_file_prompt(self, app_name: str, feature_desc: str, filename: str, existing_files: dict = None) -> str:
        """Build prompt for single file - very explicit to avoid syntax errors"""
        
        if filename == 'models.py':
            return f"""Write ONLY Python code for Django models.py file.
App: {app_name}
Feature: {feature_desc}

Requirements:
- Import: from django.db import models
- Import: from django.contrib.auth import get_user_model
- Line: User = get_user_model()
- Create 1-2 model classes
- Each model needs: __str__ method, Meta class with ordering
- ForeignKey to User must have related_name parameter
- Use auto_now_add=True for timestamps
- Maximum 20 lines total

Write complete valid Python code only. No explanations. No markdown."""

        elif filename == 'admin.py':
            # Extract model names from models.py if it exists
            model_names = []
            if existing_files and 'models.py' in existing_files:
                import re
                models_code = existing_files['models.py']
                # Find all class definitions that inherit from models.Model
                model_names = re.findall(r'class (\w+)\(models\.Model\):', models_code)
            
            models_list = ', '.join(model_names) if model_names else 'YourModel'
            
            return f"""Write ONLY Python code for Django admin.py file.
App: {app_name}
Models available: {models_list}

Requirements:
- Import: from django.contrib import admin
- Import: from .models import {models_list}
- Register ONLY the models listed above
- Use @admin.register decorator for each model
- Add list_display with 2-3 fields that exist in the model
- Maximum 15 lines total

Write complete valid Python code only. No explanations. No markdown."""

        elif filename == 'views.py':
            # Extract model names from models.py if it exists
            model_names = []
            if existing_files and 'models.py' in existing_files:
                import re
                models_code = existing_files['models.py']
                model_names = re.findall(r'class (\w+)\(models\.Model\):', models_code)
            
            models_list = ', '.join(model_names) if model_names else 'YourModel'
            
            return f"""Write ONLY Python code for Django views.py file.
App: {app_name}
Models available: {models_list}

Requirements:
- Import: from rest_framework import viewsets
- Import: from .models import {models_list}
- Create viewset classes ONLY for the models listed above
- Set queryset = ModelName.objects.all()
- Maximum 15 lines total

Write complete valid Python code only. No explanations. No markdown."""

        elif filename == 'urls.py':
            return f"""Write ONLY Python code for Django urls.py file.

Requirements:
- Line 1: from django.urls import path
- Line 2: (blank)
- Line 3: urlpatterns = [
- Line 4: (4 spaces)# Add URL patterns here
- Line 5: ]

Write exactly these 5 lines. No explanations. No markdown."""

        elif filename == 'apps.py':
            return f"""Write ONLY Python code for Django apps.py file.
App: {app_name}

Requirements:
- Line 1: from django.apps import AppConfig
- Line 2: (blank)
- Line 3: class {app_name.title().replace('_', '')}Config(AppConfig):
- Line 4: (4 spaces)default_auto_field = 'django.db.models.BigAutoField'
- Line 5: (4 spaces)name = 'apps.{app_name}'

Write exactly these 5 lines. No explanations. No markdown."""

        return f"Generate {filename} for {app_name}"
    
    def _fix_import_mismatches(self, files: dict, app_name: str) -> dict:
        """Fix import mismatches and field references between files"""
        if 'models.py' not in files:
            return files
        
        import re
        
        # Extract actual model names and their fields from models.py
        models_code = files['models.py']
        actual_models = re.findall(r'class (\w+)\(models\.Model\):', models_code)
        
        if not actual_models:
            return files
        
        print(f"  Found models: {', '.join(actual_models)}")
        
        # Extract fields for each model
        model_fields = {}
        for model_name in actual_models:
            # Find the model class definition
            model_pattern = rf'class {model_name}\(models\.Model\):(.*?)(?=class |\Z)'
            model_match = re.search(model_pattern, models_code, re.DOTALL)
            if model_match:
                model_body = model_match.group(1)
                # Find all field definitions (field_name = models.FieldType)
                # Match: field_name = models.Something(...)
                # Don't match: on_delete, related_name, etc (these are parameters)
                field_lines = re.findall(r'^\s+(\w+)\s*=\s*models\.\w+Field', model_body, re.MULTILINE)
                # Always include 'id' and limit to first 3 actual fields
                if field_lines:
                    # Filter out common non-field names
                    actual_fields = [f for f in field_lines if f not in ['on_delete', 'related_name', 'blank', 'null']]
                    model_fields[model_name] = ['id'] + actual_fields[:3]
                else:
                    model_fields[model_name] = ['id']
        
        print(f"  Model fields: {model_fields}")
        
        # Fix admin.py imports and list_display
        if 'admin.py' in files:
            admin_code = files['admin.py']
            
            # Fix imports
            import_match = re.search(r'from \.models import (.+)', admin_code)
            if import_match:
                imported = import_match.group(1)
                fixed_import = f"from .models import {', '.join(actual_models)}"
                admin_code = admin_code.replace(f"from .models import {imported}", fixed_import)
            
            # Fix list_display for each model
            for model_name in actual_models:
                if model_name in model_fields:
                    fields = model_fields[model_name]
                    # Create the list_display string
                    fields_str = "', '".join(fields)
                    new_list_display = f"list_display = ('{fields_str}')"
                    
                    # Find and replace list_display for this model
                    admin_code = re.sub(
                        rf"(@admin\.register\({model_name}\).*?)list_display\s*=\s*\([^)]+\)",
                        rf"\1{new_list_display}",
                        admin_code,
                        flags=re.DOTALL
                    )
            
            # Remove registrations for non-existent models
            for line in admin_code.split('\n'):
                if '@admin.register(' in line:
                    for model in re.findall(r'@admin\.register\((\w+)\)', line):
                        if model not in actual_models:
                            # Remove this registration block
                            admin_code = re.sub(
                                rf'@admin\.register\({model}\).*?(?=@admin\.register|class |$)',
                                '',
                                admin_code,
                                flags=re.DOTALL
                            )
            
            files['admin.py'] = admin_code
            print(f"  Fixed admin.py imports and list_display")
        
        # Fix views.py imports
        if 'views.py' in files:
            views_code = files['views.py']
            import_match = re.search(r'from \.models import (.+)', views_code)
            if import_match:
                imported = import_match.group(1)
                fixed_import = f"from .models import {', '.join(actual_models)}"
                views_code = views_code.replace(f"from .models import {imported}", fixed_import)
                files['views.py'] = views_code
                print(f"  Fixed views.py imports")
        
        return files
    
    def _build_prompt(self, feature: str, context: Dict) -> str:
        """Build prompt based on feature"""
        project_name = context.get('project_name', 'myproject')
        
        # Get feature configuration from JSON
        features = self.prompts_config.get('features', {})
        feature_config = features.get(feature, {
            "app_name": feature,
            "description": feature
        })
        
        app_name = feature_config.get('app_name', feature)
        feature_desc = feature_config.get('description', feature)
        
        # Build the prompt using the template
        prompt_template = self.prompts_config.get('prompt_template', '')
        
        prompt = prompt_template.format(
            app_name=app_name,
            feature_description=feature_desc,
            project_name=project_name
        )
        
        return prompt
    
    def _parse_response(self, response_text: str) -> Dict:
        """Parse AI response and extract JSON with improved error handling"""
        # Remove markdown code blocks if present
        text = response_text.strip()
        
        # Remove markdown code block markers
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        
        if text.endswith("```"):
            text = text[:-3]
        
        text = text.strip()
        
        # Try direct parsing first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Try to find and extract complete JSON object
        start = text.find("{")
        if start == -1:
            raise Exception("No JSON object found in response")
        
        # Count braces to find the complete JSON
        brace_count = 0
        in_string = False
        escape_next = False
        end = start
        
        for i in range(start, len(text)):
            char = text[i]
            
            if escape_next:
                escape_next = False
                continue
            
            if char == '\\':
                escape_next = True
                continue
            
            if char == '"' and not escape_next:
                in_string = not in_string
                continue
            
            if not in_string:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end = i + 1
                        break
        
        if brace_count != 0:
            raise Exception(f"Incomplete JSON object (unmatched braces)")
        
        json_text = text[start:end]
        
        # Try parsing the extracted JSON
        try:
            return json.loads(json_text)
        except json.JSONDecodeError as e:
            # Try to fix common JSON issues
            try:
                # Fix trailing commas
                fixed = re.sub(r',(\s*[}\]])', r'\1', json_text)
                # Fix single quotes to double quotes (if not in strings)
                # This is risky but can help
                return json.loads(fixed)
            except json.JSONDecodeError:
                # Save for debugging
                with open('debug_response.json', 'w', encoding='utf-8') as f:
                    f.write(json_text)
                raise Exception(f"Failed to parse JSON: {str(e)}")
    
    def generate_base_file(self, file_type: str, project_name: str) -> str:
        """
        Generate base Django files using AI
        
        Args:
            file_type: Type of file (manage_py, settings_py, urls_py, etc.)
            project_name: Name of the Django project
            
        Returns:
            Generated file content as string
        """
        if 'base_files' not in self.prompts_config:
            raise Exception("base_files prompts not found in prompts.json")
        
        if file_type not in self.prompts_config['base_files']:
            raise Exception(f"Prompt for {file_type} not found")
        
        prompt = self.prompts_config['base_files'][file_type].replace('{project_name}', project_name)
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.0,
                        "max_tokens": 2000
                    },
                    timeout=30
                )
                
                response.raise_for_status()
                result = response.json()
                content = result['choices'][0]['message']['content'].strip()
                
                # Remove markdown code blocks
                if content.startswith("```"):
                    lines = content.split('\n')
                    # Remove first line (```python or ```) and last line (```)
                    content = '\n'.join(lines[1:-1]) if len(lines) > 2 else content
                
                return content
                
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** (attempt + 1)
                    print(f"Attempt {attempt + 1} failed for {file_type}: {str(e)}")
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"Failed to generate {file_type} after {max_retries} attempts: {str(e)}")
