import os
from dotenv import load_dotenv
from app.db.session import engine, Base
# ایمپورت مدل‌ها ضروری است تا SQLAlchmey آن‌ها را بشناسد
from app.models.all_models import User, AppSettings, Domain, DomainHistory

# بارگذاری متغیرهای محیطی
load_dotenv()

def reset_database():
    print(f"Connecting to database...")
    
    # 1. حذف تمام جداول قدیمی
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    
    # 2. ساخت مجدد جداول با ستون‌های جدید
    print("Creating new tables...")
    Base.metadata.create_all(bind=engine)
    
    print("✅ Database reset successfully! Now run your app.")

if __name__ == "__main__":
    reset_database()