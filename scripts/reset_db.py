"""Reset database to initial state - useful for development."""
import os
from dotenv import load_dotenv
from app.db.session import engine, Base
# Import models - required for SQLAlchemy to recognize them
from app.models.all_models import User, AppSettings, Domain, DomainHistory

# Load environment variables
load_dotenv()

def reset_database():
    print(f"Connecting to database...")
    
    # 1. Drop all existing tables
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    
    # 2. Create new tables with updated columns
    print("Creating new tables...")
    Base.metadata.create_all(bind=engine)
    
    print("✅ Database reset successfully! Now run your app.")

if __name__ == "__main__":
    reset_database()
