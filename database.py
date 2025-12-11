"""Database configuration and session management for the Airport Dashboard."""
import os
import logging
from contextlib import contextmanager
from typing import Generator
from urllib.parse import urlparse, urlunparse

from dotenv import load_dotenv
from sqlalchemy import create_engine, select, text, inspect
from sqlalchemy.orm import scoped_session, sessionmaker, DeclarativeBase

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()


def fix_database_url(url: str) -> str:
    """
    Fix common issues with database connection strings, particularly Supabase URLs.
    
    Handles cases where port/project ID might be incorrectly included in the hostname.
    Example: postgresql://user:pass@62947@hostname:port/db -> postgresql://user:pass@hostname:port/db
    """
    if not url:
        return url
    
    # Check if URL has multiple @ symbols in netloc (malformed)
    # Pattern: scheme://user:pass@number@hostname:port/db
    try:
        # First, try to detect if there are multiple @ symbols in the connection string
        # This indicates a malformed URL
        if url.count('@') > 1:
            # Find the scheme part
            scheme_end = url.find('://')
            if scheme_end == -1:
                return url
            
            scheme = url[:scheme_end + 3]
            rest = url[scheme_end + 3:]
            
            # Split by @ to find all parts
            parts = rest.split('@')
            
            if len(parts) >= 3:
                # Format: user:pass@number@hostname:port/db
                user_pass = parts[0]  # user:pass
                # Skip the number (parts[1])
                host_port_path = parts[2]  # hostname:port/db
                
                # Reconstruct the URL
                fixed_url = f"{scheme}{user_pass}@{host_port_path}"
                return fixed_url
        
        # Also check if hostname contains @ symbol (another malformed pattern)
        parsed = urlparse(url)
        if parsed.hostname and '@' in parsed.hostname:
            # Extract the actual hostname by removing the prefix before @
            # e.g., "62947@aws-1-ap-southeast-1.pooler.supabase.com" -> "aws-1-ap-southeast-1.pooler.supabase.com"
            actual_hostname = parsed.hostname.split('@')[-1]
            
            # Reconstruct netloc
            if parsed.username:
                if parsed.password:
                    user_pass = f"{parsed.username}:{parsed.password}"
                else:
                    user_pass = parsed.username
                corrected_netloc = f"{user_pass}@{actual_hostname}"
            else:
                corrected_netloc = actual_hostname
            
            if parsed.port:
                corrected_netloc += f":{parsed.port}"
            
            # Reconstruct the full URL
            fixed_url = urlunparse((
                parsed.scheme,
                corrected_netloc,
                parsed.path,
                parsed.params,
                parsed.query,
                parsed.fragment
            ))
            return fixed_url
        
        # If URL looks correct, return as-is
        return url
        
    except Exception:
        # If parsing fails, return original URL
        return url


# Get database URL from environment variable
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is required. "
        "Please set it in your .env file or environment."
    )

# Fix any malformed connection strings
DATABASE_URL = fix_database_url(DATABASE_URL)

# Create SQLAlchemy engine with sensible defaults for cloud databases
# Optimize pool settings for serverless (Vercel) vs traditional server
is_serverless = os.environ.get('VERCEL_ENV') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME')

if is_serverless:
    # Serverless: smaller pool, connections are short-lived
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_size=1,
        max_overflow=2,
        pool_recycle=300,  # Recycle connections after 5 minutes
        future=True,
    )
else:
    # Traditional server: larger pool for persistent connections
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        future=True,
    )


class Base(DeclarativeBase):
    """Base declarative class for ORM models."""


SessionLocal = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
)


@contextmanager
def db_session() -> Generator:
    """Provide a transactional scope around a series of operations."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db():
    """Initialize database tables and add missing columns if needed."""
    from models import User, StaffNotification  # noqa: F401

    try:
        print("🔄 Initializing database...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created/verified")
        
        # Check and add missing columns if they don't exist
        with db_session() as db:
            inspector = inspect(engine)
            columns = [col['name'] for col in inspector.get_columns('users')]
            
            # Add airport_code column if it doesn't exist
            if 'airport_code' not in columns:
                print("📝 Adding airport_code column to users table...")
                db.execute(text("ALTER TABLE users ADD COLUMN airport_code VARCHAR(10)"))
                db.commit()
                print("✅ Added airport_code column")
            
            # Add created_by column if it doesn't exist
            if 'created_by' not in columns:
                print("📝 Adding created_by column to users table...")
                db.execute(text("ALTER TABLE users ADD COLUMN created_by VARCHAR(36)"))
                db.commit()
                print("✅ Added created_by column")
            
            # Add work_assignment column if it doesn't exist
            if 'work_assignment' not in columns:
                print("📝 Adding work_assignment column to users table...")
                db.execute(text("ALTER TABLE users ADD COLUMN work_assignment VARCHAR(50)"))
                db.commit()
                print("✅ Added work_assignment column")
                
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        logger.error(f"Error initializing database: {e}", exc_info=True)
        # Try to continue anyway

