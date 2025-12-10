#!/usr/bin/env python3
"""
Deployment setup script for RefOo Quiz Maker Telegram Mini App
This script helps prepare the application for deployment.
"""

import os
import shutil
import sys

def setup_deployment():
    """Setup files for deployment"""
    print("🚀 Setting up RefOo Quiz Maker for deployment...")
    
    # Create necessary directories
    directories = ['templates', 'static']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
    
    # Copy deployment files
    deployment_files = [
        ('requirements_web.txt', 'requirements.txt'),
        ('Procfile_web', 'Procfile'),
        ('config_web.py', 'config.py')
    ]
    
    for source, destination in deployment_files:
        if os.path.exists(source):
            shutil.copy2(source, destination)
            print(f"✅ Copied {source} to {destination}")
        else:
            print(f"⚠️  Source file {source} not found")
    
    # Create .env template if it doesn't exist
    env_file = '.env'
    if not os.path.exists(env_file):
        env_template = """# RefOo Quiz Maker Configuration
SECRET_KEY=your-secret-key-here
MIN_TEXT_LENGTH=30

# Optional: Override default values
# MAX_CONTENT_LENGTH=16777216
"""
        with open(env_file, 'w') as f:
            f.write(env_template)
        print(f"✅ Created {env_file} template")
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Update .env file with your configuration")
    print("2. Test locally: python app.py")
    print("3. Deploy to your preferred platform")
    print("\nFor Heroku deployment:")
    print("  git add .")
    print("  git commit -m 'Deploy Telegram Mini App'")
    print("  git push heroku main")

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'flask',
        'pdfplumber',
        'requests',
        'werkzeug'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install -r requirements_web.txt")
        return False
    
    print("✅ All dependencies are installed")
    return True

def main():
    """Main setup function"""
    print("=" * 50)
    print("RefOo Quiz Maker - Telegram Mini App Setup")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first")
        sys.exit(1)
    
    # Setup deployment files
    setup_deployment()
    
    print("\n" + "=" * 50)
    print("Setup completed successfully! 🎉")
    print("=" * 50)

if __name__ == "__main__":
    main()
