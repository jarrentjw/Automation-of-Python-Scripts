#!/usr/bin/env python3
"""
Simple validation script to test the SharePoint automation setup.
"""
import os
import sys
from pathlib import Path
import yaml


def check_file_exists(path, description):
    """Check if a file exists."""
    if Path(path).exists():
        print(f"✓ {description}")
        return True
    else:
        print(f"✗ {description} - NOT FOUND")
        return False


def check_env_file():
    """Check if .env file is configured."""
    if not Path('.env').exists():
        print("✗ .env file not found")
        print("  Run: cp .env.example .env")
        return False
    
    print("✓ .env file exists")
    
    # Check if it has required variables
    with open('.env', 'r') as f:
        content = f.read()
    
    required_vars = [
        'SHAREPOINT_SITE_URL',
        'SHAREPOINT_CLIENT_ID',
        'SHAREPOINT_CLIENT_SECRET'
    ]
    
    missing = []
    for var in required_vars:
        if var not in content or f'{var}=your-' in content:
            missing.append(var)
    
    if missing:
        print(f"⚠ The following variables need to be configured in .env:")
        for var in missing:
            print(f"  - {var}")
        return False
    
    print("✓ .env file appears to be configured")
    return True


def check_config_yaml():
    """Check if config.yaml is valid."""
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        if 'automations' not in config:
            print("✗ config.yaml missing 'automations' key")
            return False
        
        automations = config['automations']
        if not isinstance(automations, list):
            print("✗ config.yaml 'automations' should be a list")
            return False
        
        enabled_count = sum(1 for a in automations if a.get('enabled', False))
        print(f"✓ config.yaml is valid ({enabled_count} enabled automation(s))")
        
        # Check scripts exist
        for automation in automations:
            if automation.get('enabled', False):
                script = automation.get('script', '')
                if script and not Path(script).exists():
                    print(f"⚠ Script not found: {script}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error reading config.yaml: {str(e)}")
        return False


def check_dependencies():
    """Check if dependencies are installed."""
    try:
        import requests
        import yaml
        import dotenv
        from office365.sharepoint.client_context import ClientContext
        
        print("✓ All dependencies installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {str(e)}")
        print("  Run: pip install -r requirements.txt")
        return False


def main():
    """Run validation checks."""
    print("SharePoint File Automation - Setup Validation")
    print("=" * 50)
    print()
    
    checks = []
    
    print("Checking required files...")
    checks.append(check_file_exists('requirements.txt', 'requirements.txt'))
    checks.append(check_file_exists('config.yaml', 'config.yaml'))
    checks.append(check_file_exists('main.py', 'main.py'))
    checks.append(check_file_exists('sharepoint_connector.py', 'sharepoint_connector.py'))
    checks.append(check_file_exists('sharepoint_monitor.py', 'sharepoint_monitor.py'))
    checks.append(check_file_exists('script_executor.py', 'script_executor.py'))
    print()
    
    print("Checking configuration...")
    checks.append(check_env_file())
    checks.append(check_config_yaml())
    print()
    
    print("Checking dependencies...")
    checks.append(check_dependencies())
    print()
    
    print("=" * 50)
    if all(checks):
        print("✓ All checks passed! Ready to run.")
        print("\nStart the automation:")
        print("  python main.py")
        return 0
    else:
        print("✗ Some checks failed. Please fix the issues above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
