# Installation Guide

## Install Django Project Generator Globally

### Option 1: Install from Source (Recommended for Development)

```bash
# Navigate to the project directory
cd "C:\Users\Anshul\Desktop\CLI tool 2"

# Install in editable mode (changes reflect immediately)
pip install -e .
```

### Option 2: Install Normally

```bash
# Navigate to the project directory
cd "C:\Users\Anshul\Desktop\CLI tool 2"

# Install globally
pip install .
```

### Option 3: Install with Virtual Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Unix/Mac:
source venv/bin/activate

# Install
pip install -e .
```

## Configuration

After installation, set up your API key:

```bash
# Create config directory
mkdir -p ~/.initiatep

# Copy environment template
cp .env.example ~/.initiatep/.env

# Edit with your API key
# Windows:
notepad ~/.initiatep/.env
# Unix/Mac:
nano ~/.initiatep/.env
```

Add your Groq API key:
```
GROQ_API_KEY=your_actual_groq_api_key_here
```

## Usage

Once installed, you can use `initiatep` from anywhere:

```bash
# Create a new Django project
initiatep create-project

# Or simply
initiatep
```

The tool will:
1. Ask for project name
2. Ask which features to include
3. Generate the complete Django project with AI
4. Create all necessary files and setup scripts

## Verify Installation

```bash
# Check if initiatep is installed
initiatep --help

# Check version
initiatep --version
```

## Uninstall

```bash
pip uninstall django-initiatep
```

## Troubleshooting

### Command not found

If `initiatep` is not found after installation:

1. **Check if pip bin directory is in PATH:**
   ```bash
   # Windows
   echo %PATH%
   
   # Unix/Mac
   echo $PATH
   ```

2. **Find where pip installs scripts:**
   ```bash
   python -m site --user-base
   ```

3. **Add to PATH:**
   - Windows: Add `C:\Users\YourName\AppData\Local\Programs\Python\Python3XX\Scripts` to PATH
   - Unix/Mac: Add `~/.local/bin` to PATH

### Permission Denied

On Unix/Mac, you might need:
```bash
sudo pip install -e .
```

Or install for user only:
```bash
pip install --user -e .
```

### API Key Not Found

Make sure you've created the config file:
```bash
# Check if config exists
ls ~/.initiatep/.env

# If not, create it
mkdir -p ~/.initiatep
cp .env.example ~/.initiatep/.env
```

## Development Mode

For development, use editable install:
```bash
pip install -e .
```

This way, any changes you make to the code will be reflected immediately without reinstalling.

## Update

To update after pulling new changes:
```bash
cd "C:\Users\Anshul\Desktop\CLI tool 2"
git pull  # if using git
pip install --upgrade -e .
```
