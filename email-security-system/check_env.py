#!/usr/bin/env python
"""
Check environment variables for the Email Security System.
This script verifies that all required environment variables are set.
"""

import os
import sys
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Initialize colorama
init()

# Load environment variables from .env file
load_dotenv()

# Required environment variables
required_env_vars = {
    'SQLALCHEMY_DATABASE_URI': 'Database connection string',
    'JWT_SECRET_KEY': 'Secret key for JWT authentication',
    'EMAIL_USER': 'Email account for monitoring',
    'MAIL_PASSWORD': 'Password for the email account',
    'SECRET_KEY': 'Secret key for Flask and Socket.IO'
}

# Optional environment variables
optional_env_vars = {
    'OPENAI_API_KEY': 'OpenAI API key for AI features'
}

def check_env_vars():
    print(f"{Fore.BLUE}Checking environment variables...{Style.RESET_ALL}")
    
    missing_required = []
    missing_optional = []
    
    # Check required variables
    for var, description in required_env_vars.items():
        if not os.getenv(var):
            missing_required.append((var, description))
    
    # Check optional variables
    for var, description in optional_env_vars.items():
        if not os.getenv(var):
            missing_optional.append((var, description))
    
    # Print results
    if not missing_required:
        print(f"{Fore.GREEN}✓ All required environment variables are set.{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}✗ Missing required environment variables:{Style.RESET_ALL}")
        for var, description in missing_required:
            print(f"  - {Fore.RED}{var}{Style.RESET_ALL}: {description}")
    
    if missing_optional:
        print(f"\n{Fore.YELLOW}⚠ Missing optional environment variables:{Style.RESET_ALL}")
        for var, description in missing_optional:
            print(f"  - {Fore.YELLOW}{var}{Style.RESET_ALL}: {description}")
    
    # Return status
    return len(missing_required) == 0

if __name__ == "__main__":
    success = check_env_vars()
    if not success:
        print(f"\n{Fore.RED}Please set the missing required environment variables in your .env file.{Style.RESET_ALL}")
        print(f"You can run {Fore.CYAN}python generate_keys.py{Style.RESET_ALL} to create a template .env file with secure keys.")
        sys.exit(1)
    else:
        print(f"\n{Fore.GREEN}Environment check passed! You're good to go.{Style.RESET_ALL}")
        sys.exit(0) 