#!/usr/bin/env python3
"""
Verification script to check if the scaffolder is properly set up
"""
import sys
import os
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.8+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True


def check_dependencies():
    """Check if required packages are installed"""
    required = ['typer', 'requests', 'rich', 'dotenv']
    missing = []
    
    for package in required:
        try:
            __import__(package.replace('.', '_') if '.' in package else package)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is NOT installed")
            missing.append(package)
    
    if missing:
        print("\n⚠️  Install missing packages with:")
        print("   pip install -r requirements.txt")
        return False
    return True


def check_env_file():
    """Check if .env file exists and has API key"""
    if not Path('.env').exists():
        print("❌ .env file not found")
        print("   Create it with: copy .env.example .env")
        return False
    
    print("✅ .env file exists")
    
    # Check if API key is set
    with open('.env', 'r') as f:
        content = f.read()
        if 'GROQ_API_KEY=' in content:
            # Check if it's not empty or default
            for line in content.split('\n'):
                if line.startswith('GROQ_API_KEY='):
                    key = line.split('=', 1)[1].strip().strip('"').strip("'")
                    if key and key != 'your_groq_api_key_here':
                        print("✅ GROQ_API_KEY is configured")
                        return True
                    else:
                        print("⚠️  GROQ_API_KEY is empty or default")
                        print("   Add your API key to .env file")
                        return False
    
    print("❌ GROQ_API_KEY not found in .env")
    return False


def check_file_structure():
    """Check if all required files exist"""
    required_files = [
        'main.py',
        'requirements.txt',
        '.env.example',
        'generators/__init__.py',
        'generators/ai_client.py',
        'generators/project_generator.py',
        'generators/templates.py',
    ]
    
    all_exist = True
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} is missing")
            all_exist = False
    
    return all_exist


def main():
    """Run all checks"""
    print("=" * 60)
    print("Django Project Scaffolder - Setup Verification")
    print("=" * 60)
    print()
    
    print("Checking Python version...")
    python_ok = check_python_version()
    print()
    
    print("Checking dependencies...")
    deps_ok = check_dependencies()
    print()
    
    print("Checking file structure...")
    files_ok = check_file_structure()
    print()
    
    print("Checking environment configuration...")
    env_ok = check_env_file()
    print()
    
    print("=" * 60)
    if python_ok and deps_ok and files_ok and env_ok:
        print("✅ All checks passed! You're ready to generate projects.")
        print()
        print("Run: python main.py create-project")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print()
        print("Quick fix:")
        print("1. pip install -r requirements.txt")
        print("2. copy .env.example .env")
        print("3. Edit .env and add your GROQ_API_KEY")
    print("=" * 60)


if __name__ == "__main__":
    main()
