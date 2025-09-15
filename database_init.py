"""
Database initialization script
Run this script to create the database and tables
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.database import Base, engine
from app.models import user, post, comment

def create_database():
    """Create the database if it doesn't exist"""
    # Connect to MySQL server without specifying database
    server_engine = create_engine(
        f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/"
    )
    
    with server_engine.connect() as conn:
        # Create database if it doesn't exist
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {settings.MYSQL_DATABASE}"))
        conn.commit()
        print(f"Database '{settings.MYSQL_DATABASE}' created successfully!")

def create_tables():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)
    print("All tables created successfully!")

if __name__ == "__main__":
    print("Initializing database...")
    create_database()
    create_tables()
    print("Database initialization completed!")
