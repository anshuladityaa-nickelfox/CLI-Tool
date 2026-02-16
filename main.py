#!/usr/bin/env python3
"""
Django Project Scaffolder with AI
Main CLI application using Typer
"""
import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from pathlib import Path
import os
from dotenv import load_dotenv

from generators.project_generator import DjangoProjectGenerator
from generators.ai_client import AIClient

# Load environment variables from multiple locations
# Priority: 1. Current directory, 2. User home directory
load_dotenv()  # Load from current directory .env
home_config = Path.home() / '.nfxinit' / '.env'
if home_config.exists():
    load_dotenv(home_config)  # Load from ~/.nfxinit/.env

app = typer.Typer(help="Django Project Scaffolder with AI-powered code generation")
console = Console()

__version__ = "1.0.0"

FEATURES = {
    "1": {"name": "Mail Services", "key": "mail"},
    "2": {"name": "Notification System", "key": "notification"},
    "3": {"name": "RBAC (Role-Based Access Control)", "key": "rbac"},
    "4": {"name": "Upload Documents", "key": "upload"},
    "5": {"name": "Global Error Handling", "key": "error_handling"},
    "6": {"name": "Logging System (Mail, Database, File)", "key": "logging"},
}


@app.command()
def create_project():
    """Create a new Django project with AI-generated features"""
    console.print("\n[bold cyan]🚀 Django Project Generator (Nickelfox)[/bold cyan]\n")
    
    # Check for API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        console.print("[bold red]❌ Error: GROQ_API_KEY not found[/bold red]")
        console.print("\nPlease set up your API key:")
        console.print("1. Create config directory: mkdir ~/.nfxinit")
        console.print("2. Create config file: copy .env.example ~/.nfxinit/.env")
        console.print("3. Edit ~/.nfxinit/.env and add your Groq API key")
        console.print("\nOr set it in current directory .env file")
        raise typer.Exit(1)
    
    # Get project name
    project_name = Prompt.ask("[bold green]Enter project name[/bold green]")
    if not project_name:
        console.print("[bold red]Project name cannot be empty[/bold red]")
        raise typer.Exit(1)
    
    # Get project directory
    console.print("\n[bold yellow]Project Directory:[/bold yellow]")
    console.print("  • Press Enter to create in parent directory (recommended)")
    console.print("  • Or enter a custom path (e.g., C:\\Projects or /home/user/projects)")
    
    project_dir = Prompt.ask("[bold green]Directory[/bold green]", default="")
    
    if not project_dir:
        # Default: parent directory of the platform
        current_dir = Path(__file__).parent
        project_dir = str(current_dir.parent / project_name)
        console.print(f"[dim]Using: {project_dir}[/dim]")
    else:
        # Custom path
        project_dir = str(Path(project_dir) / project_name)
        console.print(f"[dim]Using: {project_dir}[/dim]")
    
    # Select programming language
    console.print("\n[bold yellow]Select programming language:[/bold yellow]")
    console.print("1. Python (Django)")
    language_choice = Prompt.ask("Choice", choices=["1"], default="1")
    language = "python"
    
    # Select features
    console.print("\n[bold yellow]Available features:[/bold yellow]")
    for key, feature in FEATURES.items():
        console.print(f"  {key}. {feature['name']}")
    
    console.print("\n[bold cyan]How to select:[/bold cyan]")
    console.print("  • Type 'all' for all features")
    console.print("  • Type '1,2,3' for specific features (Mail, Notification, RBAC)")
    console.print("  • Type '1' for just one feature (Mail only)")
    console.print("  • Press Enter for all features (default)")
    
    features_input = Prompt.ask("\n[bold green]Features[/bold green]", default="all")
    
    selected_features = []
    if features_input.lower() == "all":
        selected_features = [f["key"] for f in FEATURES.values()]
        console.print(f"[dim]Selected: All features[/dim]")
    else:
        feature_numbers = [num.strip() for num in features_input.split(",")]
        for num in feature_numbers:
            if num in FEATURES:
                selected_features.append(FEATURES[num]["key"])
        
        if selected_features:
            feature_names = [FEATURES[num]["name"] for num in feature_numbers if num in FEATURES]
            console.print(f"[dim]Selected: {', '.join(feature_names)}[/dim]")
    
    if not selected_features:
        console.print("[bold red]❌ No valid features selected[/bold red]")
        console.print("[yellow]Please enter valid feature numbers (1-6) or 'all'[/yellow]")
        raise typer.Exit(1)
    
    # Confirm
    console.print(f"\n[bold cyan]Project Configuration:[/bold cyan]")
    console.print(f"  Directory: {project_dir}")
    console.print(f"  Name: {project_name}")
    console.print(f"  Language: {language}")
    console.print(f"  Features: {', '.join(selected_features)}")
    
    if not Confirm.ask("\nProceed with project generation?", default=True):
        console.print("[yellow]Project generation cancelled[/yellow]")
        raise typer.Exit(0)
    
    # Generate project
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Initializing AI client...", total=None)
            
            ai_client = AIClient(api_key)
            generator = DjangoProjectGenerator(project_name, selected_features, ai_client, project_dir)
            
            progress.update(task, description="Generating project structure...")
            generator.generate_project()
            
            progress.update(task, description="Setting up virtual environment...")
            generator.setup_environment()
            
            progress.update(task, description="Installing dependencies...")
            generator.install_requirements()
            
            progress.update(task, description="Running migrations...")
            generator.run_migrations()
            
            progress.update(task, description="Creating superuser...")
            generator.create_superuser()
            
            progress.update(task, description="Complete!")
        
        console.print(f"\n[bold green]✅ Project '{project_name}' created successfully![/bold green]")
        console.print(f"\n[bold cyan]Project Details:[/bold cyan]")
        console.print(f"  Location: {project_dir}")
        console.print(f"  Superuser: {project_name}.com")
        console.print(f"  Password: admin123")
        
        # Ask if user wants to start the server
        if Confirm.ask("\n[bold yellow]Start development server now?[/bold yellow]", default=True):
            console.print(f"\n[bold cyan]Starting server at http://127.0.0.1:8000[/bold cyan]")
            console.print("[dim]Press Ctrl+C to stop the server[/dim]\n")
            generator.run_server()
        else:
            console.print(f"\n[bold cyan]To start the server later:[/bold cyan]")
            console.print(f"  1. cd {project_dir}")
            console.print(f"  2. venv\\Scripts\\activate  (Windows) or source venv/bin/activate (Unix)")
            console.print(f"  3. python manage.py runserver")
        console.print(f"  6. python manage.py createsuperuser")
        console.print(f"  7. python manage.py runserver")
        
    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {str(e)}[/bold red]")
        raise typer.Exit(1)


@app.command()
def version():
    """Show version information"""
    console.print(f"[bold cyan]NFXinit[/bold cyan] version [bold green]{__version__}[/bold green]")
    console.print("Django Project Generator by Nickelfox")


@app.callback(invoke_without_command=True)
def main_callback(ctx: typer.Context):
    """
    Django Project Generator by Nickelfox - Create Django projects with AI-powered features
    
    Run 'NFXinit create-project' or just 'NFXinit' to start
    """
    if ctx.invoked_subcommand is None:
        # If no subcommand, run create-project by default
        create_project()


if __name__ == "__main__":
    app()
