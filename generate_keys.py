#!/usr/bin/env python
"""
Generate secure keys for the Email Security System.
This script creates secure random keys for JWT and Flask/SocketIO.
"""

import secrets
import os
from pathlib import Path

# Check if .env already exists
env_file = Path(".env")

if env_file.exists():
    print("Warning: .env file already exists.")
    overwrite = input("Do you want to overwrite it? (y/n): ")
    if overwrite.lower() != "y":
        print("Exiting without changes.")
        exit(0)

# Generate secure keys
jwt_secret_key = secrets.token_hex(32)
secret_key = secrets.token_hex(32)

# Create or update .env file
with open(env_file, "w") as f:
    f.write(f"""# JWT Secret Key 
JWT_SECRET_KEY={jwt_secret_key}

# Email Configuration
EMAIL_USER=your_email_here@gmail.com
MAIL_PASSWORD=your_email_password_here

# SocketIO secret key
SECRET_KEY={secret_key}

# OpenAI API Key (if needed)
OPENAI_API_KEY=your_openai_api_key_here
""")

print(f"Created .env file with secure keys.")
print("IMPORTANT: Please update EMAIL_USER, MAIL_PASSWORD, and OPENAI_API_KEY with your own values.")
print("           Never commit the .env file to version control.") 