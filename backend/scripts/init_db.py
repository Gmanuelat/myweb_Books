#!/usr/bin/env python3
"""
Database initialization script
Creates all tables
"""
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Book, UserLibrary, ReadingProgress, Favorite, ReadingGoal


def init_db():
    """Initialize the database"""
    app = create_app()

    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully!")

        # Print table info
        print("\nCreated tables:")
        for table in db.metadata.tables:
            print(f"  - {table}")


if __name__ == '__main__':
    init_db()
