# Security Measures

This document outlines the security measures implemented in the Email Security System project.

## Environment Variables

All sensitive information is stored in environment variables, including:
- Database connection strings
- JWT secret keys
- Email credentials
- API keys

## Environment Files

- `.env` files are excluded from version control via `.gitignore`
- Example environment files (`.env.example`) are provided as templates
- The `generate_keys.py` script creates secure random keys for JWT and Flask/SocketIO

## Docker Security

- Docker images use specific versions of base images
- Non-root users are used in containers where possible
- Minimal dependencies are installed
- Multi-stage builds reduce attack surface in production images
- No sensitive data stored in Docker layers

## Authentication

- JWT (JSON Web Token) is used for API authentication
- Tokens have configurable expiration times
- CORS (Cross-Origin Resource Sharing) is properly configured
- Password reset functionality uses secure tokens with expiration

## Database Security

- No hardcoded database credentials
- Database files are excluded from version control
- SQLite database is stored in a Docker volume for persistence
- Input validation to prevent SQL injection

## Email Processing

- Email credentials are loaded from environment variables
- IMAP connections use SSL for encryption
- Error handling prevents exposing sensitive information
- Content scanning for potentially malicious attachments

## Frontend Security

- API URL is loaded from environment variables
- WebSocket connections include authentication
- Error messages don't expose sensitive information
- Content Security Policy (CSP) headers to prevent XSS

## Development Practices

- The `check_env.py` script verifies that all required environment variables are set
- Comprehensive `.gitignore` file prevents accidental commits of sensitive files
- Dependencies are pinned to specific versions for reproducibility
- Regular security audits of dependencies

## Deployment

- Docker Compose is used for easy and consistent deployment
- Environment variables are passed to containers at runtime
- Docker volumes are used for persistent data storage
- Health checks to ensure service availability 