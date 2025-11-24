from sqlalchemy import Column, Integer, String, Boolean
from app.db.session import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    disabled = Column(Boolean, default=False)
    role = Column(String, default="user")

class AppSettings(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True, index=True)
    telegram_bot_token = Column(String, nullable=True)
    telegram_chat_id = Column(String, nullable=True)
    proxy_url = Column(String, nullable=True)
    mattermost_url = Column(String, nullable=True)
    
    # تنظیمات پیش‌فرض (Global)
    ssl_danger_days = Column(Integer, default=7)
    ssl_warning_days = Column(Integer, default=30)
    domain_danger_days = Column(Integer, default=14)
    domain_warning_days = Column(Integer, default=60)

class Domain(Base):
    __tablename__ = "domains"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)
    
    # --- تنظیمات اختصاصی هر دامنه (اختیاری) ---
    # اگر خالی باشند (Null)، از تنظیمات Global استفاده می‌شود
    custom_ssl_danger = Column(Integer, nullable=True)
    custom_ssl_warning = Column(Integer, nullable=True)
    custom_domain_danger = Column(Integer, nullable=True)
    custom_domain_warning = Column(Integer, nullable=True)