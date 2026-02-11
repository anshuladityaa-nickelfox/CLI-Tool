# Django Project Generator (initiatep)

AI-powered Django project scaffolder using Groq's Llama 3.3 model.

## Features

- 🤖 **AI-Powered**: Uses Llama 3.3 to generate Django code
- 📦 **6 Built-in Features**: Mail, Notifications, RBAC, Uploads, Error Handling, Logging
- ⚡ **Fast Setup**: Generate complete Django projects in minutes
- 🔧 **Production Ready**: Includes Docker, setup scripts, and best practices
- 🎯 **Customizable**: Select only the features you need

## Quick Start

### 1. Install

```bash
# Clone or download this repository
cd "CLI tool 2"

# Install globally
pip install -e .
```

### 2. Configure API Key

Get your free Groq API key from: https://console.groq.com/keys

```bash
# Create config directory
mkdir ~/.initiatep

# Copy template
cp .env.example ~/.initiatep/.env

# Edit and add your API key
# Windows: notepad ~/.initiatep/.env
# Linux/Mac: nano ~/.initiatep/.env
```

Add your key:
```
GROQ_API_KEY=your_actual_groq_api_key_here
```

### 3. Generate a Project

```bash
# Run from anywhere
initiatep

# Or explicitly
initiatep create-project
```

Follow the prompts:
- Enter project name
- Select features (1,2,3 or 'all')
- Confirm and generate!

## Available Features

1. **Mail Services** - Email sending functionality
2. **Notification System** - User notifications
3. **RBAC** - Role-Based Access Control
4. **Upload Documents** - File upload management
5. **Global Error Handling** - Centralized error handling
6. **Logging System** - Application logging

## Feature Selection Examples

```bash
# All features
Features [all]: all

# Just mail and notifications
Features [all]: 1,2

# Only RBAC
Features [all]: 3

# Custom combination
Features [all]: 1,3,5,6
```

## What Gets Generated

```
your_project/
├── apps/                    # Your selected features
│   ├── mail_service/
│   ├── notifications/
│   └── rbac/
├── your_project/
│   ├── settings.py         # Configured
│   └── urls.py            # Routes added
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── setup.bat/sh           # Automated setup
└── SETUP.md              # Instructions
```

## After Generation

```bash
cd your_project

# Quick start (automated)
./quickstart.sh  # Linux/Mac
quickstart.bat   # Windows

# Or manual setup
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Commands

```bash
# Generate project
initiatep
initiatep create-project

# Show version
initiatep version

# Show help
initiatep --help

# Verify setup
python verify_setup.py
```

## Requirements

- Python 3.8+
- Groq API key (free tier available)
- Internet connection (for AI generation)

## How It Works

1. **AI Generation**: Uses Llama 3.3 to generate Django code file-by-file
2. **Validation**: Automatically validates Python syntax
3. **Coordination**: Ensures imports and references match between files
4. **Integration**: Configures settings, URLs, and requirements automatically

## Troubleshooting

### Command not found

Add Python scripts to PATH:
- Windows: `C:\Users\YourName\AppData\Local\Programs\Python\Python3XX\Scripts`
- Linux/Mac: `~/.local/bin`

### API Key not found

```bash
# Check config exists
ls ~/.initiatep/.env

# If not, create it
mkdir -p ~/.initiatep
cp .env.example ~/.initiatep/.env
# Edit and add your GROQ_API_KEY
```

### Generation fails

- Check your API key is valid
- Ensure internet connection
- Try again (AI generation can occasionally fail)

## Development

```bash
# Install in editable mode
pip install -e .

# Make changes to code
# Changes reflect immediately (no reinstall needed)

# Run directly
python main.py create-project
```

## Project Structure

```
CLI tool 2/
├── generators/              # Core generation logic
│   ├── ai_client.py        # Groq API integration
│   ├── project_generator.py # Project scaffolding
│   ├── code_validator.py   # Syntax validation
│   ├── templates.py        # Base Django templates
│   └── gitignore_template.py
├── main.py                 # CLI entry point
├── prompts.json           # AI prompts configuration
├── setup.py               # Package configuration
├── requirements.txt       # Dependencies
└── README.md             # This file
```

## Configuration

### Prompts

Edit `prompts.json` to customize AI prompts for each feature.

### Models

Change model in `generators/ai_client.py`:
```python
self.model = "llama-3.3-70b-versatile"  # Current
# Or try: "mixtral-8x7b-32768", "gemma2-9b-it"
```

## License

MIT License - Feel free to use and modify!

## Support

For issues or questions:
1. Check `USAGE_GUIDE.md` for detailed usage
2. Run `python verify_setup.py` to check configuration
3. Review generated `SETUP.md` in your project

## Credits

- Built with [Typer](https://typer.tiangolo.com/) for CLI
- Powered by [Groq](https://groq.com/) AI
- Uses [Llama 3.3](https://www.llama.com/) model

---

**Happy Coding! 🚀**
