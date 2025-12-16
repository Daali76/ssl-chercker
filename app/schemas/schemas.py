from typing import Optional
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"

class UserResponse(BaseModel):
    id: int
    username: str
    disabled: bool
    role: str
    class Config:
        from_attributes = True

class DomainCreate(BaseModel):
    url: str
    ssl_danger: Optional[int] = None
    ssl_warning: Optional[int] = None
    domain_danger: Optional[int] = None
    domain_warning: Optional[int] = None
    notify_warning: Optional[bool] = True
    notify_critical: Optional[bool] = True
    monitor_ssl: Optional[bool] = True
    monitor_domain: Optional[bool] = True

class DomainUpdate(BaseModel):
    ssl_danger: Optional[int] = None
    ssl_warning: Optional[int] = None
    domain_danger: Optional[int] = None
    domain_warning: Optional[int] = None
    notify_warning: Optional[bool] = True
    notify_critical: Optional[bool] = True
    monitor_ssl: Optional[bool] = True
    monitor_domain: Optional[bool] = True

class RoleUpdate(BaseModel):
    role: str

class SettingsUpdate(BaseModel):
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    proxy_url: Optional[str] = None
    mattermost_url: Optional[str] = None
    slack_webhook_url: Optional[str] = None
    custom_webhook_url: Optional[str] = None
    shodan_api_key: Optional[str] = None
    
    ssl_danger_days: Optional[int] = None
    ssl_warning_days: Optional[int] = None
    domain_danger_days: Optional[int] = None
    domain_warning_days: Optional[int] = None
    check_interval_hours: Optional[int] = None
    
    msg_ssl_warning: Optional[str] = None
    msg_ssl_danger: Optional[str] = None
    msg_dom_warning: Optional[str] = None
    msg_dom_danger: Optional[str] = None

class TelegramTestRequest(BaseModel):
    token: str
    chat_id: str

class WebhookTestRequest(BaseModel):
    webhook_url: str
    
class MattermostTestRequest(BaseModel):
    webhook_url: str