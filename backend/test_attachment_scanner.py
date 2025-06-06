import os
import sys
import logging
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pathlib import Path
from dotenv import load_dotenv

# Import our attachment analyzer
from email_processor import analyze_attachment

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('test_attachment_scanner')

# Load environment variables
load_dotenv()

def create_test_email_with_attachment(attachment_filename, attachment_content, content_type="application/octet-stream"):
    """Create a test email with the specified attachment"""
    msg = MIMEMultipart()
    msg['Subject'] = f'Test email with {attachment_filename} attachment'
    msg['From'] = 'test@example.com'
    msg['To'] = 'recipient@example.com'
    
    # Add some text content
    text = MIMEText("This is a test email with an attachment.")
    msg.attach(text)
    
    # Add the attachment
    attachment = MIMEApplication(attachment_content)
    attachment.add_header('Content-Disposition', 'attachment', filename=attachment_filename)
    attachment.add_header('Content-Type', content_type)
    msg.attach(attachment)
    
    return msg

def test_attachment_scanner():
    """Test the attachment scanner with various types of attachments"""
    test_cases = [
        # Safe document
        {
            'filename': 'document.pdf',
            'content': b'%PDF-1.5\nThis is a fake PDF file content',
            'content_type': 'application/pdf',
            'expected_safe': True
        },
        # Executable file (should be flagged)
        {
            'filename': 'setup.exe',
            'content': b'This is a fake executable content',
            'content_type': 'application/x-msdownload',
            'expected_safe': False
        },
        # Script file (should be flagged)
        {
            'filename': 'script.vbs',
            'content': b'Dim x\nx = MsgBox("Hello")',
            'content_type': 'application/x-vbs',
            'expected_safe': False
        },
        # Very large file (should be flagged)
        {
            'filename': 'large_file.zip',
            'content': b'0' * (11 * 1024 * 1024),  # 11MB
            'content_type': 'application/zip',
            'expected_safe': False
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        # Create test email
        email_msg = create_test_email_with_attachment(
            test_case['filename'],
            test_case['content'],
            test_case['content_type']
        )
        
        # Find the attachment part
        attachment_part = None
        for part in email_msg.walk():
            if part.get_filename() == test_case['filename']:
                attachment_part = part
                break
        
        if not attachment_part:
            logger.error(f"Failed to find attachment part for {test_case['filename']}")
            continue
        
        # Analyze the attachment
        analysis = analyze_attachment(attachment_part)
        
        # Check if result matches expectation
        result = {
            'filename': test_case['filename'],
            'expected_safe': test_case['expected_safe'],
            'actual_safe': analysis['is_safe'],
            'reason': analysis['reason'],
            'passed': analysis['is_safe'] == test_case['expected_safe']
        }
        
        results.append(result)
        
        # Log the result
        if result['passed']:
            logger.info(f"✅ PASSED: {result['filename']} - Expected: {result['expected_safe']}, Got: {result['actual_safe']}")
        else:
            logger.error(f"❌ FAILED: {result['filename']} - Expected: {result['expected_safe']}, Got: {result['actual_safe']}")
            logger.error(f"  Reason: {result['reason']}")
    
    # Print summary
    passed = sum(1 for r in results if r['passed'])
    total = len(results)
    logger.info(f"\nSummary: {passed}/{total} tests passed")
    
    return results

if __name__ == '__main__':
    logger.info("Starting attachment scanner tests...")
    results = test_attachment_scanner()
    
    # Exit with non-zero code if any test failed
    if not all(r['passed'] for r in results):
        sys.exit(1)
    
    logger.info("All tests passed!")
    sys.exit(0) 
