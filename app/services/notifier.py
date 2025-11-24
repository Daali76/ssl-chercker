import logging
import aiohttp
from sqlalchemy.orm import Session
from app.models.all_models import AppSettings
from app.db.session import SessionLocal

# می‌توان مقدار پیش‌فرض را از کانفیگ خواند، اما اینجا برای سادگی hardcode شده یا باید به config.py اضافه شود
ENV_MATTERMOST_URL = "" 

async def send_telegram(message: str, settings: AppSettings):
    if not settings.telegram_bot_token or not settings.telegram_chat_id: return
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    payload = {"chat_id": settings.telegram_chat_id, "text": message, "parse_mode": "Markdown"}
    try:
        async with aiohttp.ClientSession() as session:
            proxy = settings.proxy_url if settings.proxy_url else None
            async with session.post(url, json=payload, proxy=proxy) as resp:
                if resp.status != 200: logging.error(f"Telegram Error: {await resp.text()}")
    except Exception as e: logging.error(f"Telegram Connection Error: {e}")

async def send_mattermost(message: str, webhook_url: str):
    if not webhook_url or "YOUR_WEBHOOK_URL" in webhook_url: return
    try:
        payload = {"text": message, "username": "SSL-Bot", "icon_url": "https://cdn-icons-png.flaticon.com/512/2092/2092063.png"}
        async with aiohttp.ClientSession() as session:
            await session.post(webhook_url, json=payload)
    except Exception as e: logging.error(f"Mattermost Error: {e}")

async def notify_all(message: str):
    db = SessionLocal()
    settings = db.query(AppSettings).first()
    if settings:
        await send_telegram(message, settings)
        mm_url = settings.mattermost_url if settings.mattermost_url else ENV_MATTERMOST_URL
        await send_mattermost(message, mm_url)
    db.close()