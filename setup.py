"""
Setup script for Kasparro Agentic Facebook Analyst.
"""

import os
import subprocess
from pathlib import Path


def create_directories():
    """Create necessary directories."""
    directories = [
        "data",
        "reports",
        "logs",
        "prompts",
        "config",
        "src/agents"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")


def create_env_file():
    """Create .env file from template if it doesn't exist."""
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            import shutil
            shutil.copy(".env.example", ".env")
            print("✓ Created .env file from template")
            print("⚠ Please add your GROQ_API_KEY to .env")
        else:
            with open(".env", "w") as f:
                f.write("GROQ_API_KEY=your_groq_api_key_here\n")
            print("✓ Created .env file")
            print("⚠ Please add your GROQ_API_KEY to .env")


def install_dependencies():
    """Install Python dependencies."""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.run(
            ["pip", "install", "-r", "requirements.txt"],
            check=True
        )
        print("✓ Dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing dependencies: {e}")
    except FileNotFoundError:
        print("⚠ pip not found. Please install dependencies manually:")
        print("  pip install -r requirements.txt")


def main():
    """Main setup function."""
    print("🚀 Setting up Kasparro Agentic Facebook Analyst\n")
    
    create_directories()
    create_env_file()
    
    print("\n📦 Install dependencies? (y/n): ", end="")
    response = input().lower().strip()
    if response == 'y':
        install_dependencies()
    else:
        print("⏭ Skipping dependency installation")
        print("Run: pip install -r requirements.txt")
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Add your GROQ_API_KEY to .env")
    print("2. Place your data in data/sample_fb_ads.csv")
    print("3. Run: python run.py")


if __name__ == "__main__":
    main()


