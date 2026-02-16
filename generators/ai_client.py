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
    
    def __init__(self, api_key: str, language: str = "django"):
        self.api_key = api_key
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        # Use llama3 - better at following instructions than qwen
        self.model = "llama-3.3-70b-versatile"
        self.language = language
        
        # Load prompts from JSON file
        prompts_file = Path(__file__).parent.parent / 'prompts.json'
        with open(prompts_file, 'r') as f:
            all_prompts = json.load(f)
            # Get language-specific prompts
            self.prompts_config = all_prompts.get(language, all_prompts.get("django"))
    
    def generate_code(self, feature: str, context: Dict) -> Dict:
        """
        Generate code for a specific feature using AI (works for Django/Next.js/NestJS)
        
        Args:
            feature: Feature name (mail, notification, rbac, button, auth, etc.)
            context: Additional context for code generation
            
        Returns:
            Dictionary containing generated files and their content
        """
        print(f"[INFO] Generating {feature} using AI (llama-3.3) for {self.language}...")
        
        # Use batch generation (file by file) - NO FALLBACK
        return self._generate_in_batches(feature, context)
    
    # Keep old method name for backward compatibility
    def generate_django_code(self, feature: str, context: Dict) -> Dict:
        """Backward compatibility wrapper"""
        return self.generate_code(feature, context)
    
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
        
        # Get feature configuration based on language
        if self.language == "django":
            features = self.prompts_config.get('features', {})
            feature_config = features.get(feature, {
                "app_name": feature,
                "description": feature
            })
            
            app_name = feature_config.get('app_name', feature)
            feature_desc = feature_config.get('description', feature)
            
            # Files to generate for Django
            files_to_generate = ['models.py', 'admin.py', 'views.py', 'urls.py', 'apps.py']
            
        elif self.language == "nextjs":
            components = self.prompts_config.get('components', {})
            component_config = components.get(feature, {
                "component_name": feature.title(),
                "description": feature
            })
            
            app_name = component_config.get('component_name', feature.title())
            feature_desc = component_config.get('description', feature)
            
            # Files to generate for Next.js
            files_to_generate = ['component.tsx', 'types.ts', 'styles.module.css']
            
        elif self.language == "nestjs":
            modules = self.prompts_config.get('modules', {})
            module_config = modules.get(feature, {
                "module_name": feature,
                "description": feature
            })
            
            app_name = module_config.get('module_name', feature)
            feature_desc = module_config.get('description', feature)
            
            # Files to generate for NestJS
            files_to_generate = ['module.ts', 'controller.ts', 'service.ts', 'entity.ts', 'dto.ts']
        
        else:
            raise Exception(f"Unsupported language: {self.language}")
        
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
                # Use minimal code for failed file (Django only)
                if self.language == "django":
                    from generators.code_validator import get_minimal_code
                    generated_files[filename] = get_minimal_code(filename, app_name)
                else:
                    # For Next.js/NestJS, just use empty/minimal content
                    generated_files[filename] = f"// TODO: Implement {filename}"
        
        # Fix import mismatches between files (Django only)
        if self.language == "django":
            generated_files = self._fix_import_mismatches(generated_files, app_name)
        
        print(f"[SUCCESS] Generated {app_name}")
        
        # Return in expected format
        if self.language == "django":
            return {
                "app_name": app_name,
                "files": generated_files,
                "settings": "",
                "requirements": [],
                "instructions": f"{app_name} generated"
            }
        elif self.language == "nextjs":
            return {
                "component_name": app_name,
                "files": generated_files,
                "dependencies": [],
                "instructions": f"{app_name} component generated"
            }
        elif self.language == "nestjs":
            return {
                "module_name": app_name,
                "files": generated_files,
                "dependencies": [],
                "instructions": f"{app_name} module generated"
            }
    
    def _generate_single_file(self, app_name: str, feature_desc: str, filename: str, project_name: str, existing_files: dict = None) -> str:
        """Generate a single file using AI"""
        prompt = self._build_single_file_prompt(app_name, feature_desc, filename, existing_files)
        
        # Determine system message based on language
        if self.language == "django":
            system_msg = "You are a Python code generator. You ONLY output valid Python code. Never add explanations, comments, or markdown. Just pure Python code that can be executed directly."
        elif self.language == "nextjs":
            system_msg = "You are a TypeScript/React code generator. You ONLY output valid TypeScript/React code. Never add explanations or markdown. Just pure code that can be used directly."
        elif self.language == "nestjs":
            system_msg = "You are a TypeScript/NestJS code generator. You ONLY output valid TypeScript code. Never add explanations or markdown. Just pure code that can be used directly."
        else:
            system_msg = "You are a code generator. You ONLY output valid code. Never add explanations or markdown."
        
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
                            "content": system_msg
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.1 if self.language in ["nextjs", "nestjs"] else 0.0,  # Slightly higher for TS to get better structure
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
                    elif code.startswith("```typescript") or code.startswith("```tsx"):
                        code = code[code.find('\n')+1:]  # Skip first line
                    elif code.startswith("```css"):
                        code = code[6:]
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
                        
                        # Start collecting when we see code patterns
                        if self.language == "django":
                            if stripped.startswith(('from ', 'import ', 'class ', 'def ', '@')):
                                in_code = True
                        elif self.language in ["nextjs", "nestjs"]:
                            # For TypeScript/React, be more lenient
                            if (stripped.startswith(('import ', 'export ', 'const ', 'function ', 'class ', 'interface ', 'type ', '@', '//', '/*', "'use client'", '"use client"')) or
                                (stripped.startswith('.') and filename.endswith('.css')) or  # CSS
                                (in_code and stripped)):  # Once started, keep all non-empty lines
                                in_code = True
                        
                        if in_code:
                            code_lines.append(line)
                    
                    if code_lines:
                        code = '\n'.join(code_lines)
                    
                    # Basic validation for Python only
                    if self.language == "django":
                        try:
                            compile(code, '<string>', 'exec')
                            print(f"    ✓ Valid Python")
                        except SyntaxError as e:
                            print(f"    ✗ Syntax error: {e}")
                            raise Exception(f"Invalid Python: {e}")
                    elif self.language in ["nextjs", "nestjs"] and filename.endswith('.tsx'):
                        # Basic validation for React components
                        if 'export default function' not in code and 'export default' not in code:
                            print(f"    ✗ Missing export default")
                            raise Exception("Missing export default")
                        
                        # Fix React component structure
                        if filename == 'component.tsx':
                            fixed_code = self._fix_react_component(code, app_name)
                            if fixed_code != code:
                                code = fixed_code
                                print(f"    ⚠ Fixed React component structure")
                        
                        print(f"    ✓ Code generated")
                    else:
                        # For TypeScript/CSS, just check it's not empty
                        if code:
                            print(f"    ✓ Code generated")
                    
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
        """Build prompt for single file - language-specific"""
        
        if self.language == "django":
            return self._build_django_file_prompt(app_name, feature_desc, filename, existing_files)
        elif self.language == "nextjs":
            return self._build_nextjs_file_prompt(app_name, feature_desc, filename, existing_files)
        elif self.language == "nestjs":
            return self._build_nestjs_file_prompt(app_name, feature_desc, filename, existing_files)
        else:
            return f"Generate {filename} for {app_name}"
    
    def _build_django_file_prompt(self, app_name: str, feature_desc: str, filename: str, existing_files: dict = None) -> str:
        """Build prompt for Django file - very explicit to avoid syntax errors"""
        
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
    
    def _build_nextjs_file_prompt(self, component_name: str, component_desc: str, filename: str, existing_files: dict = None) -> str:
        """Build prompt for Next.js component file"""
        
        if filename == 'component.tsx':
            return f"""Generate a valid React TypeScript component file.

Component Name: {component_name}
Description: {component_desc}

CRITICAL REQUIREMENTS - Follow this EXACT structure:

Line 1: 'use client';
Line 2: (blank)
Line 3: import React from 'react';
Line 4: (blank if no hooks needed, or import {{ useState }} from 'react'; if needed)
Lines after: Component function

Component structure:
export default function {component_name}() {{
  // hooks here if needed
  
  return (
    <div className="...">
      {{/* JSX content */}}
    </div>
  );
}}

Rules:
- MUST start with 'use client';
- MUST import React
- MUST have export default function
- MUST have single root JSX element
- Use Tailwind CSS classes
- Maximum 35 lines
- NO explanations, NO markdown, ONLY code

Output valid TypeScript/React code only."""

        elif filename == 'types.ts':
            return f"""Write ONLY TypeScript types/interfaces for {component_name} component.

Requirements:
- Export interface for component props
- Export any other needed types
- Maximum 15 lines

Write complete valid TypeScript code only. No explanations. No markdown."""

        elif filename == 'styles.module.css':
            return f"""Write ONLY CSS for {component_name} component.

Requirements:
- Use CSS modules syntax (.className)
- Maximum 20 lines
- Modern CSS

Write complete valid CSS code only. No explanations. No markdown."""

        return f"Generate {filename} for {component_name}"
    
    def _build_nestjs_file_prompt(self, module_name: str, module_desc: str, filename: str, existing_files: dict = None) -> str:
        """Build prompt for NestJS module file"""
        
        if filename == 'module.ts':
            return f"""Write ONLY TypeScript code for NestJS module.
Module: {module_name}
Description: {module_desc}

Requirements:
- Import @Module from '@nestjs/common'
- Import controller and service
- @Module decorator with imports, controllers, providers
- Export class {module_name.title()}Module
- Maximum 15 lines

Write complete valid TypeScript code only. No explanations. No markdown."""

        elif filename == 'controller.ts':
            return f"""Write ONLY TypeScript code for NestJS controller.
Module: {module_name}

Requirements:
- Import decorators from '@nestjs/common'
- @Controller decorator
- Inject service in constructor
- 2-3 basic endpoints (GET, POST)
- Maximum 25 lines

Write complete valid TypeScript code only. No explanations. No markdown."""

        elif filename == 'service.ts':
            return f"""Write ONLY TypeScript code for NestJS service.
Module: {module_name}

Requirements:
- Import @Injectable from '@nestjs/common'
- @Injectable decorator
- 2-3 basic methods
- Maximum 20 lines

Write complete valid TypeScript code only. No explanations. No markdown."""

        elif filename == 'entity.ts':
            return f"""Write ONLY TypeScript code for TypeORM entity.
Module: {module_name}

Requirements:
- Import decorators from 'typeorm'
- @Entity decorator
- @PrimaryGeneratedColumn, @Column decorators
- 3-5 fields
- Maximum 20 lines

Write complete valid TypeScript code only. No explanations. No markdown."""

        elif filename == 'dto.ts':
            return f"""Write ONLY TypeScript code for DTOs.
Module: {module_name}

Requirements:
- Import decorators from 'class-validator'
- Create DTO class
- Use validation decorators
- Maximum 15 lines

Write complete valid TypeScript code only. No explanations. No markdown."""

        return f"Generate {filename} for {module_name}"
    
    def _fix_react_component(self, code: str, component_name: str) -> str:
        """Fix common React component issues"""
        lines = code.split('\n')
        fixed_lines = []
        
        # Ensure 'use client' is first
        has_use_client = any("'use client'" in line or '"use client"' in line for line in lines)
        if not has_use_client:
            fixed_lines.append("'use client';")
            fixed_lines.append("")
        
        # Ensure React import exists
        has_react_import = any('import React' in line for line in lines)
        react_import_added = False
        
        for line in lines:
            # Skip if we already added use client
            if not has_use_client and ("'use client'" in line or '"use client"' in line):
                continue
            
            # Add React import after use client if missing
            if not has_react_import and not react_import_added:
                if "'use client'" in line or '"use client"' in line or (fixed_lines and 'use client' in fixed_lines[0]):
                    if line.strip() == '':
                        fixed_lines.append(line)
                        fixed_lines.append("import React from 'react';")
                        react_import_added = True
                        continue
            
            fixed_lines.append(line)
        
        # If React import still not added, add it after use client
        if not has_react_import and not react_import_added:
            for i, line in enumerate(fixed_lines):
                if 'use client' in line:
                    fixed_lines.insert(i + 1, '')
                    fixed_lines.insert(i + 2, "import React from 'react';")
                    break
        
        return '\n'.join(fixed_lines)
    
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
        Generate base files using AI (Django/Next.js/NestJS)
        
        Args:
            file_type: Type of file (manage_py, settings_py, package_json, etc.)
            project_name: Name of the project
            
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
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a code generator. Output ONLY valid code with NO explanations, NO comments, NO markdown. Just pure code that can be executed directly."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.0,
                        "max_tokens": 2000
                    },
                    timeout=30
                )
                
                if response.status_code == 429:
                    # Rate limit hit - wait longer
                    if attempt < max_retries - 1:
                        wait_time = 10 * (attempt + 1)  # 10s, 20s, 30s
                        print(f"Rate limit hit. Waiting {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    raise Exception(f"Rate limit exceeded after {max_retries} attempts")
                
                response.raise_for_status()
                result = response.json()
                content = result['choices'][0]['message']['content'].strip()
                
                # Aggressive cleaning of markdown and explanations
                lines = content.split('\n')
                cleaned_lines = []
                in_code_block = False
                code_started = False
                
                for line in lines:
                    stripped = line.strip()
                    
                    # Skip markdown code block markers
                    if stripped.startswith('```'):
                        in_code_block = not in_code_block
                        continue
                    
                    # Skip explanatory text before code starts
                    if not code_started:
                        # Detect code start patterns
                        if (stripped.startswith('{') or  # JSON
                            stripped.startswith('from ') or stripped.startswith('import ') or  # Python
                            stripped.startswith('const ') or stripped.startswith('module.exports') or  # JS
                            stripped.startswith('/**') or  # JSDoc
                            stripped.startswith('FROM ') or stripped.startswith('WORKDIR ') or  # Dockerfile
                            stripped.startswith('version:') or stripped.startswith('services:')):  # docker-compose
                            code_started = True
                            cleaned_lines.append(line)
                        continue
                    
                    # Once code started, keep everything except obvious explanations
                    if not stripped.startswith('Here') and not stripped.startswith('This '):
                        cleaned_lines.append(line)
                
                content = '\n'.join(cleaned_lines).strip()
                
                # If still has explanatory text at the start, try to extract just the code
                if content.startswith('Here') or 'example' in content[:100].lower():
                    # Try to find the actual code block
                    if '{' in content:
                        # JSON or JS object
                        start = content.find('{')
                        # Find matching closing brace
                        brace_count = 0
                        for i in range(start, len(content)):
                            if content[i] == '{':
                                brace_count += 1
                            elif content[i] == '}':
                                brace_count -= 1
                                if brace_count == 0:
                                    content = content[start:i+1]
                                    break
                
                return content
                
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** (attempt + 1)
                    print(f"Attempt {attempt + 1} failed for {file_type}: {str(e)}")
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"Failed to generate {file_type} after {max_retries} attempts: {str(e)}")
