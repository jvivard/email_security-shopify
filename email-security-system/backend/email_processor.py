import imaplib
import email
from email import policy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle
from datetime import datetime
import importlib
import os
from dotenv import load_dotenv

load_dotenv()

IMAP_SERVER = 'imap.gmail.com'
EMAIL_USER = os.getenv('EMAIL_USER', 'wwe2k14matches@gmail.com')
EMAIL_PASS = os.getenv('MAIL_PASSWORD', 'vgxj jbvl iacd vqig')  # Replace with your App Password

# Load or train the classifier (unchanged from your original code)
try:
    with open('spam_model.pkl', 'rb') as f:
        clf = pickle.load(f)
    with open('vectorizer.pkl', 'rb') as f:
        vectorizer = pickle.load(f)
except FileNotFoundError:
    corpus = ['spam text', 'phishing text', 'normal text']
    labels = [1, 2, 0]
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(corpus)
    clf = MultinomialNB()
    clf.fit(X, labels)
    with open('spam_model.pkl', 'wb') as f:
        pickle.dump(clf, f)
    with open('vectorizer.pkl', 'wb') as f:
        pickle.dump(vectorizer, f)

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
    
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_USER, EMAIL_PASS)
    
    # Explicitly set mailbox name with quotes as a bytes object
    mailbox_name = b'"[Gmail]/All Mail"'
    print(f"Selecting mailbox: {mailbox_name.decode()}")
    status, data = mail.select(mailbox_name) # type: ignore
    if status != 'OK':
        print(f"Failed to select mailbox: {data}")
        mail.logout()
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
    
    status, data = mail.search(None, *search_criteria)
    if status != 'OK':
        print(f"Search failed: {data}")
        mail.logout()
        return 0
    
    email_ids = data[0].split()
    if not email_ids:
        print(f"No unseen emails in {category_name} matching the date criteria.")
        mail.logout()
        return 0
    
    # Limit the number of emails processed
    email_ids = email_ids[:max_emails]
    print(f"Processing {len(email_ids)} emails from {category_name}...")
    
    processed_count = 0
    for num in email_ids:
        try:
            _, msg_data = mail.fetch(num, '(RFC822)')
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email, policy=policy.default)
            sender = msg['From']
            subject = msg['Subject']
            
            # Get the email body
            plain_body = msg.get_body(preferencelist=('plain',))
            if plain_body:
                body = plain_body.get_content()
            else:
                html_body = msg.get_body(preferencelist=('html',))
                body = html_body.get_content() if html_body else ''
            
            # Extract the email date from the Date header
            email_date_str = msg.get('Date', '')
            if email_date_str:
                try:
                    email_date = datetime.strptime(email_date_str, '%a, %d %b %Y %H:%M:%S %z')
                except ValueError:
                    email_date = datetime.now()
            else:
                email_date = datetime.now()
            
            # Process with ML model
            X = vectorizer.transform([body])
            prediction = clf.predict(X)[0]
            is_spam = prediction == 1
            is_phishing = prediction == 2
            
            # Create and save the email record
            email_record = Email(
                sender=sender, 
                subject=subject, 
                body=body,
                is_spam=is_spam, 
                is_phishing=is_phishing,
                category=category_name, 
                email_date=email_date
            )
            db.session.add(email_record)
            db.session.commit()
            
            # Send an alert if it's a phishing email
            send_alert(email_record)
            
            # Mark the email as read in Gmail
            mail.store(num, '+FLAGS', '\\Seen')
            processed_count += 1
        except Exception as e:
            print(f"Error processing email: {e}")
    
    print(f"Finished processing {processed_count} emails from {category_name}.")
    mail.logout()
    return processed_count

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
        
        categories = parameters.get('categories', ['primary'])
        max_emails = int(parameters.get('max_emails', 10))
        
        # Parse dates if provided
        start_date = None
        if 'start_date' in parameters and parameters['start_date']:
            start_date = datetime.fromisoformat(parameters['start_date'].replace('Z', '+00:00'))
        
        end_date = None
        if 'end_date' in parameters and parameters['end_date']:
            end_date = datetime.fromisoformat(parameters['end_date'].replace('Z', '+00:00'))
        
        results = {}
        
        with app.app_context():
            for category in categories:
                # Map category value to display name
                category_name = category.capitalize()
                results[category] = fetch_and_process_emails_from_category(
                    category_search=category.lower(),
                    category_name=category_name,
                    max_emails=max_emails,
                    start_date=start_date,
                    end_date=end_date
                )
        
        return {
            'success': True,
            'message': 'Emails processed successfully',
            'results': results
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error processing emails: {str(e)}'
        }

if __name__ == '__main__':
    with app.app_context():
        # Process only emails from Feb 22, 2025, or later
        start_date = datetime(2025, 2, 18)  # February 22, 2025
        fetch_and_process_emails_from_category('primary', 'Primary', start_date=start_date)
        fetch_and_process_emails_from_category('promotions', 'Promotions', start_date=start_date)
        fetch_and_process_emails_from_category('social', 'Social', start_date=start_date)
    print("All categories processed. Exiting.")