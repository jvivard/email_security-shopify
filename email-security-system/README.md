# Email Security System

A full-stack application for monitoring and securing email communications. Features include spam detection, phishing detection, and a real-time security dashboard.

## Features

- Real-time email monitoring
- Spam and phishing detection
- Security dashboard with metrics
- Email categorization and management
- WebSocket-based real-time updates

## Technology Stack

- **Backend**: Flask, SQLAlchemy, Socket.IO
- **Frontend**: Next.js, React, TypeScript, Tailwind CSS
- **ML**: Scikit-learn for spam/phishing detection
- **Database**: SQLite (can be configured for other databases)
- **Docker**: Containerized deployment

## Setup

### Environment Variables

1. Copy the example environment file:
   ```
   cp .env.example .env
   ```

2. Fill in the required environment variables in `.env`:
   - JWT_SECRET_KEY: Secret key for JWT authentication
   - EMAIL_USER: Email account for monitoring
   - MAIL_PASSWORD: Password for the email account
   - SECRET_KEY: Secret key for Flask and Socket.IO
   - OPENAI_API_KEY: (Optional) If using OpenAI features

### Docker Setup (Recommended)

Build and run using Docker Compose:

```bash
docker-compose up --build
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

### Manual Setup

#### Backend

1. Set up a Python virtual environment:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the Flask application:
   ```bash
   flask run
   ```

#### Frontend

1. Install Node.js dependencies:
   ```bash
   cd next-frontend
   npm install
   ```

2. Create `.env.local` file with:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:5000
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

## Development

### Adding Sample Data

Visit `http://localhost:5000/add-sample-data` to add sample emails to the database.

### Email Processing

The email processor can be configured through the dashboard interface or by calling:
```
POST /run-email-processor
```
with JSON parameters to customize the fetch criteria.

## Security Notes

- All sensitive information is stored in environment variables
- No hardcoded credentials in the codebase
- Authentication is required for all API endpoints
- Real-time monitoring of phishing attempts

## Screenshots

### Security Dashboard
![Security Dashboard](assets/images/dashboard.png)
*The main dashboard showing email security metrics and controls*

### Recent Detections
![Recent Detections](assets/images/detections.png)
*List of recently detected security threats in emails*

### Spam Test Tool
![Spam Test Tool](assets/images/spam-test.png)
*AI-powered tool to analyze text for spam characteristics*

## Tech Stack

### Backend
- **Framework**: Flask
- **Database**: PostgreSQL
- **Real-time Communication**: Socket.IO
- **Authentication**: JWT (JSON Web Token)
- **Email Processing**: IMAP (for fetching emails)
- **Machine Learning**: scikit-learn (for spam and phishing detection)

### Frontend
- **Framework**: Next.js 15.1.7
- **UI Library**: React 19
- **Styling**: Tailwind CSS
- **UI Components**: Material-UI (@mui/material)
- **Icons**: Lucide React
- **Real-time Updates**: Socket.IO Client

## Features

- **Email Monitoring**: Connect to email accounts and monitor incoming emails
- **Threat Detection**: Automatic detection of spam and phishing emails
- **Real-time Alerts**: Instant notifications for security threats
- **Email Organization**: Categorization and organization of emails
- **Security Dashboard**: Visual representation of email security metrics
- **Customizable Processing**: Configure which email categories to process and how many emails to fetch

## Backend Packages

- **Flask**: Web framework
- **Flask-SQLAlchemy**: ORM for database operations
- **Flask-JWT-Extended**: JWT authentication
- **Flask-Mail**: Email handling
- **Flask-CORS**: Cross-origin resource sharing
- **Flask-SocketIO**: WebSocket support for real-time communication
- **scikit-learn**: Machine learning library for email classification
- **imaplib**: Library for IMAP protocol
- **pickle**: Object serialization for ML models

## Frontend Packages

- **Next.js**: React framework
- **React**: UI library
- **@mui/material**: Material Design components
- **@emotion/react & @emotion/styled**: Styling solution
- **socket.io-client**: Client for Socket.IO
- **lucide-react**: Icon library
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework

## Setup & Installation

### Prerequisites
- Python 3.8+ with Conda
- Node.js 14+
- PostgreSQL database

### Backend Setup
1. Create and activate Conda environment:
   ```
   conda create -n emailsec python=3.8
   conda activate emailsec
   ```

2. Install required Python packages:
   ```
   pip install flask flask-sqlalchemy flask-jwt-extended flask-mail flask-cors flask-socketio scikit-learn imaplib psycopg2-binary python-dotenv eventlet
   ```

3. Set up PostgreSQL database:
   ```
   CREATE DATABASE emailsec;
   ```

4. Configure email credentials in `backend/.env` file with the following variables:
   ```
   # Database configuration
   SQLALCHEMY_DATABASE_URI=postgresql://username:password@localhost:5432/emailsec
   
   # JWT configuration
   JWT_SECRET_KEY=your_jwt_secret_key_here
   
   # Email configuration
   EMAIL_USER=your_email@gmail.com
   MAIL_PASSWORD=your_app_password_here
   
   # OpenAI API configuration
   OPENAI_API_KEY=your_openai_api_key_here
   
   # Security settings
   SECRET_KEY=your_flask_secret_key_here
   ```

5. Run the Flask server:
   ```
   cd backend
   python app.py
   ```

### Frontend Setup
1. Install dependencies:
   ```
   cd next-frontend
   npm install
   ```

2. Run the development server:
   ```
   npm run dev
   ```

3. Access the application at http://localhost:3000

## Usage

1. Log in to the system
2. Navigate to the Security Dashboard
3. Use the Email Processor Control panel to fetch and analyze emails
4. View security metrics and recent detections
5. Receive real-time alerts for potential threats

## Security Considerations

- Email credentials should be stored in environment variables (see backend/.env)
- JWT secret keys should be changed in production
- Consider implementing proper authentication for API endpoints

## License

This project is proprietary and confidential. 