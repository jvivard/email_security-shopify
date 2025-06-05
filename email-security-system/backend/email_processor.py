import imaplib
import email
from email import policy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle
from datetime import datetime
import importlib
import os
import logging
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('email_processor')

# Load environment variables
load_dotenv()

# Constants
IMAP_SERVER = 'imap.gmail.com'
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASS = os.getenv('MAIL_PASSWORD')
MODEL_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
SPAM_MODEL_PATH = MODEL_DIR / 'spam_model.pkl'
VECTORIZER_PATH = MODEL_DIR / 'vectorizer.pkl'

# Check for required environment variables
if not EMAIL_USER or not EMAIL_PASS:
    logger.warning("Email credentials (EMAIL_USER, MAIL_PASSWORD) are not configured in environment variables.")
    logger.warning("Email processing functionality will not work without these credentials.")

# Load or train the classifier
try:
    logger.info(f"Loading ML models from {MODEL_DIR}")
    with open(SPAM_MODEL_PATH, 'rb') as f:
        clf = pickle.load(f)
    with open(VECTORIZER_PATH, 'rb') as f:
        vectorizer = pickle.load(f)
    logger.info("ML models loaded successfully")
except FileNotFoundError as e:
    logger.warning(f"Model files not found: {e}. Training new models...")
    corpus = ['spam text', 'phishing text', 'normal text']
    labels = [1, 2, 0]
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(corpus)
    clf = MultinomialNB()
    clf.fit(X, labels)
    
    # Save trained models
    try:
        with open(SPAM_MODEL_PATH, 'wb') as f:
            pickle.dump(clf, f)
        with open(VECTORIZER_PATH, 'wb') as f:
            pickle.dump(vectorizer, f)
        logger.info("New ML models trained and saved successfully")
    except Exception as e:
        logger.error(f"Failed to save ML models: {e}")

def fetch_and_process_emails_from_category(category_search, category_name, max_emails=10, start_date=None, end_date=None):
    """
    Fetch and process emails from a specific Gmail category
    
    Parameters:
    - category_search: The Gmail category to search (primary, promotions, social)
    - category_name: Display name for the category
    - max_emails: Maximum number of emails to fetch
    - start_date: Optional datetime to filter emails after this date
    - end_date: Optional datetime to filter emails before this date
    
    Returns:
    - Count of processed emails
    """
    # Import here to avoid circular imports
    from app import db, Email, send_alert
    
    if not EMAIL_USER or not EMAIL_PASS:
        logger.error("Email credentials (EMAIL_USER, MAIL_PASSWORD) are not configured in .env file.")
        return 0

    mail = None
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        
        # Explicitly set mailbox name with quotes as a bytes object
        mailbox_name = b'"[Gmail]/All Mail"'
        logger.info(f"Selecting mailbox: {mailbox_name.decode()}")
        status, data = mail.select(mailbox_name) # type: ignore
        if status != 'OK':
            logger.error(f"Failed to select mailbox: {data}")
            return 0
        
        # Build the search query with date filters if provided
        search_criteria = ['UNSEEN']
        date_filter = ""
        
        if start_date:
            # Format the date for Gmail's after: operator (YYYY/MM/DD)
            start_date_str = start_date.strftime('%Y/%m/%d')
            date_filter += f"after:{start_date_str} "
        
        if end_date:
            # Format the date for Gmail's before: operator (YYYY/MM/DD)
            end_date_str = end_date.strftime('%Y/%m/%d')
            date_filter += f"before:{end_date_str} "
        
        # Add date filter if any
        if date_filter:
            search_criteria.append(f'X-GM-RAW "{date_filter.strip()}"')
        
        # Add category filter
        search_criteria.append(f'X-GM-RAW "category:{category_search}"')
        
        logger.info(f"Searching with criteria: {search_criteria}")
        status, data = mail.search(None, *search_criteria)
        if status != 'OK':
            logger.error(f"Search failed: {data}")
            return 0
        
        email_ids = data[0].split()
        if not email_ids:
            logger.info(f"No unseen emails in {category_name} matching the date criteria.")
            return 0
        
        # Limit the number of emails processed
        email_ids = email_ids[:max_emails]
        logger.info(f"Processing {len(email_ids)} emails from {category_name}...")
        
        processed_count = 0
        for num in email_ids:
            try:
                status, msg_data = mail.fetch(num, '(RFC822)')
                if status != 'OK' or not msg_data or not msg_data[0]:
                    logger.error(f"Failed to fetch email with ID {num}")
                    continue
                    
                raw_email = msg_data[0][1]
                if not raw_email:
                    logger.error(f"No raw email data for ID {num}")
                    continue
                
                # Ensure raw_email is bytes
                if not isinstance(raw_email, bytes):
                    logger.error(f"Raw email data is not bytes for ID {num}")
                    continue
                    
                msg = email.message_from_bytes(raw_email, policy=policy.default)
                sender = msg.get('From', 'Unknown Sender')
                subject = msg.get('Subject', 'No Subject')
                
                logger.info(f"Processing email: {subject}")
                
                # Get the email body
                plain_body = msg.get_body(preferencelist=('plain',))
                if plain_body:
                    body = plain_body.get_content()
                else:
                    html_body = msg.get_body(preferencelist=('html',))
                    body = html_body.get_content() if html_body else ''
                
                # Ensure we have a valid body for processing
                if not body:
                    logger.warning(f"Could not extract body content from email: {subject}")
                    body = "No content available"
                
                # Extract the email date from the Date header
                email_date_str = msg.get('Date', '')
                if email_date_str:
                    try:
                        email_date = datetime.strptime(email_date_str, '%a, %d %b %Y %H:%M:%S %z')
                    except ValueError:
                        logger.warning(f"Could not parse email date: {email_date_str}. Using current time.")
                        email_date = datetime.now()
                else:
                    email_date = datetime.now()
                
                # Process with ML model
                X = vectorizer.transform([body])
                prediction = clf.predict(X)[0]
                is_spam = prediction == 1
                is_phishing = prediction == 2
                
                # Check for attachments
                has_dangerous_attachment = False
                attachment_warnings = []
                attachment_data = []
                
                # Process attachments
                for part in msg.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get('Content-Disposition') is None:
                        continue
                    if part.get_filename() is not None:
                        analysis = analyze_attachment(part)
                        attachment_data.append(analysis)
                        if not analysis["is_safe"]:
                            has_dangerous_attachment = True
                            attachment_warnings.append(f"{analysis['filename']}: {analysis['reason']}")
                            logger.warning(f"Dangerous attachment found in email: {subject} - {analysis['reason']}")
                
                if has_dangerous_attachment:
                    is_phishing = True  # Mark emails with dangerous attachments as phishing
                
                if is_spam:
                    logger.warning(f"Spam detected in email: {subject}")
                if is_phishing:
                    logger.warning(f"PHISHING ATTEMPT detected in email: {subject}")
                
                # Create and save the email record
                email_record = Email(
                    sender=sender, 
                    subject=subject, 
                    body=body,
                    is_spam=is_spam, 
                    is_phishing=is_phishing,
                    category=category_name, 
                    email_date=email_date,
                    attachment_info=json.dumps(attachment_data) if attachment_data else None
                )
                db.session.add(email_record)
                db.session.commit()
                
                # Send an alert if it's a phishing email
                if is_phishing:
                    send_alert(email_record)
                
                # Mark the email as read in Gmail
                mail.store(num, '+FLAGS', '\\Seen')
                processed_count += 1
            except Exception as e:
                logger.error(f"Error processing email: {e}", exc_info=True)
                # Try to continue with the next email
                continue
        
        logger.info(f"Finished processing {processed_count} emails from {category_name}.")
        return processed_count
    except imaplib.IMAP4.error as e:
        logger.error(f"IMAP error: {e}", exc_info=True)
        return 0
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 0
    finally:
        if mail:
            try:
                mail.logout()
                logger.info("IMAP connection closed")
            except Exception as e:
                logger.error(f"Error closing IMAP connection: {e}")

def process_emails(parameters):
    """
    Process emails based on the provided parameters
    
    Parameters:
    - parameters: dict containing:
        - categories: list of categories to fetch (primary, promotions, social)
        - max_emails: maximum number of emails to fetch per category
        - start_date: ISO format date string (YYYY-MM-DD) to start fetching from
        - end_date: ISO format date string (YYYY-MM-DD) to end fetching at
    
    Returns:
    - dict with results of the processing
    """
    try:
        # Import app here to avoid circular imports
        from app import app
        
        logger.info(f"Starting email processing with parameters: {parameters}")
        
        # Validate parameters
        if not isinstance(parameters, dict):
            logger.error("Invalid parameters format: not a dictionary")
            return {
                'success': False,
                'message': 'Invalid parameters format'
            }
        
        # Extract and validate parameters
        categories = parameters.get('categories', ['primary'])
        if not isinstance(categories, list):
            logger.warning(f"Invalid categories parameter: {categories}. Using default ['primary']")
            categories = ['primary']
        
        try:
            max_emails = int(parameters.get('max_emails', 10))
            if max_emails < 1:
                logger.warning(f"Invalid max_emails value: {max_emails}. Using default 10")
                max_emails = 10
        except (ValueError, TypeError):
            logger.warning(f"Could not parse max_emails: {parameters.get('max_emails')}. Using default 10")
            max_emails = 10
        
        # Parse dates if provided
        start_date = None
        if 'start_date' in parameters and parameters['start_date']:
            try:
                start_date = datetime.fromisoformat(parameters['start_date'].replace('Z', '+00:00'))
                logger.info(f"Using start date: {start_date}")
            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid start_date: {parameters['start_date']}. Error: {e}")
        
        end_date = None
        if 'end_date' in parameters and parameters['end_date']:
            try:
                end_date = datetime.fromisoformat(parameters['end_date'].replace('Z', '+00:00'))
                logger.info(f"Using end date: {end_date}")
            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid end_date: {parameters['end_date']}. Error: {e}")
        
        results = {}
        
        with app.app_context():
            for category in categories:
                # Map category value to display name
                category_name = category.capitalize()
                logger.info(f"Processing category: {category_name}")
                results[category] = fetch_and_process_emails_from_category(
                    category_search=category.lower(),
                    category_name=category_name,
                    max_emails=max_emails,
                    start_date=start_date,
                    end_date=end_date
                )
        
        logger.info(f"Email processing completed. Results: {results}")
        return {
            'success': True,
            'message': 'Emails processed successfully',
            'results': results
        }
    except Exception as e:
        logger.error(f"Error processing emails: {e}", exc_info=True)
        return {
            'success': False,
            'message': f'Error processing emails: {str(e)}'
        }

def analyze_attachment(attachment):
    """
    Analyze an email attachment for potential security threats
    
    Parameters:
    - attachment: Email attachment object
    
    Returns:
    - dict with analysis results
    """
    try:
        filename = attachment.get_filename()
        if not filename:
            return {"is_safe": True, "reason": "No filename"}
            
        content_type = attachment.get_content_type()
        size = len(attachment.get_payload(decode=True))
        
        # Check for potentially dangerous file extensions
        dangerous_extensions = ['.exe', '.bat', '.cmd', '.msi', '.js', '.vbs', '.ps1', '.jar', '.scr']
        is_dangerous_ext = any(filename.lower().endswith(ext) for ext in dangerous_extensions)
        
        # Check for unusually large attachments (over 10MB)
        is_large = size > 10 * 1024 * 1024
        
        # Check for suspicious content types
        suspicious_types = ['application/x-msdownload', 'application/x-msdos-program', 'application/x-javascript']
        is_suspicious_type = content_type in suspicious_types
        
        is_safe = not (is_dangerous_ext or is_suspicious_type)
        
        reason = []
        if is_dangerous_ext:
            reason.append("Potentially dangerous file extension")
        if is_suspicious_type:
            reason.append("Suspicious content type")
        if is_large:
            reason.append("Unusually large attachment")
            
        return {
            "filename": filename,
            "content_type": content_type,
            "size": size,
            "is_safe": is_safe,
            "reason": ", ".join(reason) if reason else "No threats detected"
        }
    except Exception as e:
        logger.error(f"Error analyzing attachment: {e}")
        return {"is_safe": False, "reason": f"Analysis error: {str(e)}"}

if __name__ == '__main__':
    try:
        from app import app
        with app.app_context():
            # Process only emails from Feb 22, 2025, or later
            start_date = datetime(2025, 2, 18)
            logger.info(f"Running standalone with start_date={start_date}")
            fetch_and_process_emails_from_category('primary', 'Primary', start_date=start_date)
            fetch_and_process_emails_from_category('promotions', 'Promotions', start_date=start_date)
            fetch_and_process_emails_from_category('social', 'Social', start_date=start_date)
        logger.info("All categories processed. Exiting.")
    except Exception as e:
        logger.critical(f"Critical error in standalone mode: {e}", exc_info=True)
        sys.exit(1)
