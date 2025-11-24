from typing import Optional, List
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

# --- جدید: مدل ویرایش دامنه ---
class DomainUpdate(BaseModel):
    ssl_danger: Optional[int] = None
    ssl_warning: Optional[int] = None
    domain_danger: Optional[int] = None
    domain_warning: Optional[int] = None
# ------------------------------

class RoleUpdate(BaseModel):
    role: str

class SettingsUpdate(BaseModel):
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    proxy_url: Optional[str] = None
    mattermost_url: Optional[str] = None
    ssl_danger_days: Optional[int] = None
    ssl_warning_days: Optional[int] = None
    domain_danger_days: Optional[int] = None
    domain_warning_days: Optional[int] = None