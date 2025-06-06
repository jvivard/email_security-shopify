import os
import sys
import logging
import psycopg2
from dotenv import load_dotenv
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('migrate_db')

# Load environment variables
load_dotenv()

def run_migrations():
    """
    Run database migrations from schema.sql
    """
    try:
        # Get database connection string from environment
        db_uri = os.getenv('SQLALCHEMY_DATABASE_URI')
        if not db_uri:
            logger.error("Database URI not found in environment variables")
            return False

        # Connect to the database
        logger.info("Connecting to database...")
        conn = psycopg2.connect(db_uri)
        cursor = conn.cursor()
        
        # Read the schema.sql file
        schema_path = Path(os.path.dirname(os.path.abspath(__file__))) / 'schema.sql'
        logger.info(f"Reading schema from {schema_path}")
        
        with open(schema_path, 'r') as f:
            sql = f.read()
        
        # Execute the SQL
        logger.info("Executing schema migrations...")
        cursor.execute(sql)
        conn.commit()
        
        logger.info("Migrations completed successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error running migrations: {e}")
        return False
    
    finally:
        if 'conn' in locals() and conn:
            conn.close()
            logger.info("Database connection closed")

if __name__ == '__main__':
    success = run_migrations()
    if success:
        logger.info("Database migration completed successfully")
        sys.exit(0)
    else:
        logger.error("Database migration failed")
        sys.exit(1) 
