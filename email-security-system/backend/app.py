import os
import sys
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('app')

# Load environment variables from .env file
load_dotenv()

# Check for required environment variables
required_env_vars = [
    'SQLALCHEMY_DATABASE_URI',
    'JWT_SECRET_KEY',
    'EMAIL_USER',
    'MAIL_PASSWORD',
    'SECRET_KEY'
]

missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
    logger.error("Please create a .env file with the required variables or set them in your environment.")
    # Continue with defaults for development, but log warnings

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
from flask_mail import Mail, Message
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from sqlalchemy import event
from datetime import datetime
import importlib
import requests
import json

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)

# Helper function to handle CORS options requests
def handle_cors_options(allowed_methods):
    response = app.make_default_options_response()
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    response.headers['Access-Control-Allow-Methods'] = allowed_methods
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
mail = Mail(app)
socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000", async_mode='eventlet')

# Email Model
class Email(db.Model):
    __tablename__ = 'emails'
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255))
    body = db.Column(db.Text)
    received_at = db.Column(db.DateTime, default=db.func.now())
    email_date = db.Column(db.DateTime)
    is_spam = db.Column(db.Boolean, default=False)
    is_phishing = db.Column(db.Boolean, default=False)
    category = db.Column(db.String(50))
    is_important = db.Column(db.Boolean, default=False)
    is_archived = db.Column(db.Boolean, default=False)
    is_read = db.Column(db.Boolean, default=False)

    def serialize(self):
        return {
            'id': self.id,
            'sender': self.sender,
            'subject': self.subject,
            'is_spam': self.is_spam,
            'is_phishing': self.is_phishing,
            'category': self.category,
            'email_date': self.email_date.isoformat() if self.email_date else None,
            'is_important': self.is_important,
            'is_archived': self.is_archived,
            'is_read': self.is_read
        }

# Database event listener for real-time updates
def email_created_listener(mapper, connection, target):
    socketio.emit('new_email', target.serialize(), namespace='/emails')

event.listen(Email, 'after_insert', email_created_listener)

# WebSocket Handlers
@socketio.on('connect', namespace='/emails')
def handle_connect():
    emit('connection_response', {'status': 'connected', 'message': 'Successfully connected to email stream'})

@socketio.on('disconnect', namespace='/emails')
def handle_disconnect():
    print('Client disconnected from email stream')

# Existing Routes (Updated with SocketIO)
@app.route('/emails', methods=['OPTIONS', 'GET'])
def get_emails():
    if request.method == 'OPTIONS':
        return handle_cors_options('GET, OPTIONS')

    emails = Email.query.all()
    return jsonify([e.serialize() for e in emails])

# Add endpoint to mark emails as important
@app.route('/emails/<int:email_id>/mark-important', methods=['OPTIONS', 'PUT'])
def mark_email_important(email_id):
    if request.method == 'OPTIONS':
        return handle_cors_options('PUT, OPTIONS')
    
    email = Email.query.get(email_id)
    if not email:
        return jsonify({'error': 'Email not found'}), 404
    
    # Toggle the is_important flag
    email.is_important = not email.is_important
    db.session.commit()
    
    # Emit socket event with updated email
    socketio.emit('email_updated', email.serialize(), namespace='/emails')
    
    return jsonify(email.serialize())

# Add endpoint to toggle archive status
@app.route('/emails/<int:email_id>/toggle-archive', methods=['OPTIONS', 'PUT'])
def toggle_archive_email(email_id):
    if request.method == 'OPTIONS':
        return handle_cors_options('PUT, OPTIONS')
    
    email = Email.query.get(email_id)
    if not email:
        return jsonify({'error': 'Email not found'}), 404
    
    # Toggle the is_archived flag
    email.is_archived = not email.is_archived
    db.session.commit()
    
    # Emit socket event with updated email
    socketio.emit('email_updated', email.serialize(), namespace='/emails')
    
    return jsonify(email.serialize())

# Add endpoint to toggle read status
@app.route('/emails/<int:email_id>/toggle-read', methods=['OPTIONS', 'PUT'])
def toggle_read_email(email_id):
    if request.method == 'OPTIONS':
        return handle_cors_options('PUT, OPTIONS')
    
    email = Email.query.get(email_id)
    if not email:
        return jsonify({'error': 'Email not found'}), 404
    
    # Toggle the is_read flag
    email.is_read = not email.is_read
    db.session.commit()
    
    # Emit socket event with updated email
    socketio.emit('email_updated', email.serialize(), namespace='/emails')
    
    return jsonify(email.serialize())

# Add endpoint to delete an email
@app.route('/emails/<int:email_id>', methods=['OPTIONS', 'DELETE'])
def delete_email(email_id):
    if request.method == 'OPTIONS':
        return handle_cors_options('DELETE, OPTIONS')
    
    email = Email.query.get(email_id)
    if not email:
        return jsonify({'error': 'Email not found'}), 404
    
    # Store the ID for the socket event before deletion
    email_id = email.id
    
    # Delete the email
    db.session.delete(email)
    db.session.commit()
    
    # Emit socket event to notify of deletion
    socketio.emit('email_deleted', {'id': email_id}, namespace='/emails')
    
    return jsonify({'success': True, 'message': 'Email deleted'})

# Alert System with SocketIO Integration
def send_alert(email_record):
    if email_record.is_phishing:
        # Send email alert
        msg = Message("High-Risk Email Detected",
                      sender="wwe2k14matches@gmail.com",
                      recipients=["wwe2k14matches@gmail.com"])
        msg.body = f"Phishing email from {email_record.sender}: {email_record.subject}"
        mail.send(msg)
        
        # Real-time WebSocket alert
        socketio.emit('security_alert', {
            'type': 'phishing',
            'message': 'New phishing email detected',
            'email_id': email_record.id
        }, namespace='/alerts')

# Add new endpoint to run the email processor with configurable parameters
@app.route('/run-email-processor', methods=['POST'])
def run_email_processor():
    if request.method == 'POST':
        # Extract parameters from request
        parameters = request.get_json()
        if not parameters:
            return jsonify({'error': 'No parameters provided'}), 400

        # Import email_processor dynamically to avoid circular imports
        import email_processor
        
        # Run the email processor with the provided parameters
        result = email_processor.process_emails(parameters)
        return jsonify(result)

# Add new endpoint to add sample data
@app.route('/add-sample-data', methods=['GET'])
def add_sample_data():
    try:
        # Sample data
        sample_emails = [
            {
                'sender': 'john.doe@example.com',
                'subject': 'Meeting Tomorrow',
                'body': 'Hi team, just a reminder about our meeting tomorrow at 10 AM.',
                'received_at': datetime.now(),
                'email_date': datetime.now(),
                'is_spam': False,
                'is_phishing': False,
                'category': 'Primary',
                'is_important': True,
                'is_archived': False,
                'is_read': False
            },
            {
                'sender': 'marketing@company.com',
                'subject': 'Special Offer Inside!',
                'body': 'Limited time offer! 50% off on all products.',
                'received_at': datetime.now(),
                'email_date': datetime.now(),
                'is_spam': True,
                'is_phishing': False,
                'category': 'Promotions',
                'is_important': False,
                'is_archived': False,
                'is_read': False
            },
            {
                'sender': 'security@bankofamerica.com',
                'subject': 'Urgent: Your Account Has Been Compromised',
                'body': 'Click here to verify your account details immediately.',
                'received_at': datetime.now(),
                'email_date': datetime.now(),
                'is_spam': False,
                'is_phishing': True,
                'category': 'Primary',
                'is_important': False,
                'is_archived': False,
                'is_read': False
            }
        ]
        
        # Insert data
        for email_data in sample_emails:
            email = Email(**email_data)
            db.session.add(email)
        
        db.session.commit()
        
        # Emit socket event for each new email
        for email in Email.query.order_by(Email.id.desc()).limit(len(sample_emails)):
            socketio.emit('new_email', email.serialize(), namespace='/emails')
        
        return jsonify({'success': True, 'message': f'Added {len(sample_emails)} sample emails'})
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Add endpoint to test text for spam using OpenAI API
@app.route('/test-spam', methods=['OPTIONS', 'POST'])
def test_spam():
    if request.method == 'OPTIONS':
        return handle_cors_options('POST, OPTIONS')
    
    # Get text from request
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
    
    text_to_analyze = data['text']
    
    # OpenAI API configuration
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        return jsonify({'error': 'OpenAI API key not configured. Please set the OPENAI_API_KEY environment variable.'}), 503
    
    # Prepare request to OpenAI API
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }
    
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system", 
                "content": "You are a spam detection expert. Analyze the following text and determine if it's spam or not. Respond with just 'spam' or 'not spam' followed by a brief explanation."
            },
            {
                "role": "user", 
                "content": text_to_analyze
            }
        ],
        "temperature": 0.7
    }
    
    try:
        # Call OpenAI API
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        # Process response
        if response.status_code == 200:
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            
            # Determine if the message is spam based on AI response
            is_spam = "spam" in ai_response.lower()[:10]
            
            return jsonify({
                'text': text_to_analyze,
                'is_spam': is_spam,
                'analysis': ai_response
            })
        else:
            return jsonify({'error': f'OpenAI API error: {response.status_code}', 'details': response.text}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Use eventlet for WebSocket support
    socketio.run(app, debug=True)
