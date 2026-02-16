#!/usr/bin/env python3
"""
Initialize the database - run this once to create all tables
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.base import engine, Base
from app.models.user import User
from app.models.company import Company
from app.models.snapshot import Snapshot
from app.models.change import Change
from app.models.notification import Notification

def init_database():
    """Create all tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully!")

if __name__ == "__main__":
    init_database()