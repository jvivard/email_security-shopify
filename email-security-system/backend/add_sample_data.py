import psycopg2
from datetime import datetime

# Database connection parameters
db_params = {
    'dbname': 'emailsec',
    'user': 'postgres',
    'password': 'Kickrobotic123@',
    'host': 'localhost',
    'port': '5432'
}

try:
    # Connect to the database
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    
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
    for email in sample_emails:
        cursor.execute("""
        INSERT INTO emails 
        (sender, subject, body, received_at, email_date, is_spam, is_phishing, category, is_important, is_archived, is_read)
        VALUES 
        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            email['sender'], 
            email['subject'], 
            email['body'], 
            email['received_at'], 
            email['email_date'], 
            email['is_spam'], 
            email['is_phishing'], 
            email['category'], 
            email['is_important'], 
            email['is_archived'], 
            email['is_read']
        ))
    
    # Commit the transaction
    conn.commit()
    print("Successfully added sample data to the database!")
    
except Exception as e:
    print(f"Error: {e}")
    if 'conn' in locals():
        conn.rollback()
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close() 