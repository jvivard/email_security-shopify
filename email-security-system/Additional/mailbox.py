import imaplib

IMAP_SERVER = 'imap.gmail.com'
EMAIL_USER = 'wwe2k14matches@gmail.com'
EMAIL_PASS = 'vgxj jbvl iacd vqig'

mail = imaplib.IMAP4_SSL(IMAP_SERVER)
mail.login(EMAIL_USER, EMAIL_PASS)

# List mailboxes
status, mailboxes = mail.list()
if status == 'OK':
    for box in mailboxes:
        print(box.decode())
else:
    print("Failed to list mailboxes.")

# Select a mailbox (e.g., INBOX) to see its structure
status, data = mail.select('INBOX')
if status == 'OK':
    print("Selected INBOX successfully.")
else:
    print("Failed to select INBOX.")

mail.logout()