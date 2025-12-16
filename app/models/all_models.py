from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
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
    
    proxy_url = Column(String, nullable=True)
    check_interval_hours = Column(Integer, default=24)
    shodan_api_key = Column(String, nullable=True)

    telegram_bot_token = Column(String, nullable=True)
    telegram_chat_id = Column(String, nullable=True)
    mattermost_url = Column(String, nullable=True)
    slack_webhook_url = Column(String, nullable=True)   
    custom_webhook_url = Column(String, nullable=True)  
    
    ssl_danger_days = Column(Integer, default=7)
    ssl_warning_days = Column(Integer, default=30)
    domain_danger_days = Column(Integer, default=14)
    domain_warning_days = Column(Integer, default=60)
    
    msg_ssl_warning = Column(String, nullable=True)
    msg_ssl_danger = Column(String, nullable=True)
    msg_dom_warning = Column(String, nullable=True)
    msg_dom_danger = Column(String, nullable=True)

class Domain(Base):
    __tablename__ = "domains"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)
    
    custom_ssl_danger = Column(Integer, nullable=True)
    custom_ssl_warning = Column(Integer, nullable=True)
    custom_domain_danger = Column(Integer, nullable=True)
    custom_domain_warning = Column(Integer, nullable=True)

    notify_on_warning = Column(Boolean, default=True)
    notify_on_critical = Column(Boolean, default=True)
    monitor_ssl = Column(Boolean, default=True)
    monitor_domain = Column(Boolean, default=True)
    
    # Shodan data fields
    shodan_data = Column(JSON, nullable=True)
    shodan_last_checked = Column(DateTime, nullable=True)

    history = relationship("DomainHistory", back_populates="domain", cascade="all, delete-orphan")

class DomainHistory(Base):
    __tablename__ = "domain_history"
    id = Column(Integer, primary_key=True, index=True)
    domain_id = Column(Integer, ForeignKey("domains.id"))
    checked_at = Column(DateTime, default=datetime.utcnow)
    
    ssl_days = Column(Integer, nullable=True)
    domain_days = Column(Integer, nullable=True)
    overall_status = Column(String)
    
    domain = relationship("Domain", back_populates="history")