-- Emails table to store fetched emails
DROP TABLE IF EXISTS emails;

CREATE TABLE emails (
    id SERIAL PRIMARY KEY,
    sender VARCHAR(255) NOT NULL,
    subject VARCHAR(255),
    body TEXT,
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    email_date TIMESTAMP,
    is_spam BOOLEAN DEFAULT FALSE,
    is_phishing BOOLEAN DEFAULT FALSE,
    category VARCHAR(50),
    is_important BOOLEAN DEFAULT FALSE,
    is_archived BOOLEAN DEFAULT FALSE,
    is_read BOOLEAN DEFAULT FALSE,
    attachment_info TEXT
);

-- Add index on common query fields
CREATE INDEX idx_email_is_spam ON emails(is_spam);
CREATE INDEX idx_email_is_phishing ON emails(is_phishing);
CREATE INDEX idx_email_category ON emails(category);
CREATE INDEX idx_email_received_at ON emails(received_at);
CREATE INDEX idx_email_is_important ON emails(is_important);
CREATE INDEX idx_email_is_archived ON emails(is_archived);
CREATE INDEX idx_email_is_read ON emails(is_read);

-- Migration for existing tables (if needed)
-- This will run only if the table exists but is missing the new columns
DO $$
BEGIN
    -- Check and add is_important column if missing
    IF EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'emails'
    ) AND NOT EXISTS (
        SELECT FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'emails' 
        AND column_name = 'is_important'
    ) THEN
        ALTER TABLE emails ADD COLUMN is_important BOOLEAN DEFAULT FALSE;
    END IF;
    
    -- Check and add is_archived column if missing
    IF EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'emails'
    ) AND NOT EXISTS (
        SELECT FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'emails' 
        AND column_name = 'is_archived'
    ) THEN
        ALTER TABLE emails ADD COLUMN is_archived BOOLEAN DEFAULT FALSE;
    END IF;
    
    -- Check and add is_read column if missing
    IF EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'emails'
    ) AND NOT EXISTS (
        SELECT FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'emails' 
        AND column_name = 'is_read'
    ) THEN
        ALTER TABLE emails ADD COLUMN is_read BOOLEAN DEFAULT FALSE;
    END IF;
    
    -- Check and add attachment_info column if missing
    IF EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'emails'
    ) AND NOT EXISTS (
        SELECT FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'emails' 
        AND column_name = 'attachment_info'
    ) THEN
        ALTER TABLE emails ADD COLUMN attachment_info TEXT;
    END IF;
END
$$;

-- Blacklist table for flagged domains/senders
CREATE TABLE blacklist (
    id SERIAL PRIMARY KEY,
    entity VARCHAR(255) UNIQUE NOT NULL, -- Domain or email address
    reason VARCHAR(255),
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sender analytics table for tracking patterns
CREATE TABLE sender_analytics (
    id SERIAL PRIMARY KEY,
    sender VARCHAR(255) NOT NULL,
    email_count INTEGER DEFAULT 1,
    spam_count INTEGER DEFAULT 0,
    phishing_count INTEGER DEFAULT 0,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
