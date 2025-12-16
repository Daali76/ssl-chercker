import logging
import aiohttp
from app.models.all_models import AppSettings

logger = logging.getLogger(__name__)

# --- Main Sending Functions ---
async def send_telegram(message: str, settings: AppSettings):
    if not settings.telegram_bot_token or not settings.telegram_chat_id: return
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    payload = {"chat_id": settings.telegram_chat_id, "text": message, "parse_mode": "Markdown"}
    try:
        async with aiohttp.ClientSession() as session:
            proxy = settings.proxy_url if settings.proxy_url else None
            async with session.post(url, json=payload, proxy=proxy, timeout=10) as resp:
                if resp.status != 200: logger.error(f"Telegram Error: {await resp.text()}")
    except Exception as e: logger.error(f"Telegram Connection Error: {e}")

async def send_mattermost(message: str, webhook_url: str):
    if not webhook_url: return
    try:
        # Mattermost supports multiple payload formats
        payload = {
            "text": message,
            "username": "🔒 SSL Monitor",
            "icon_emoji": ":lock:",  # Use emoji instead of icon_url (more reliable)
            "mattermost_format": True
        }
        
        # Alternative: Use attachments for richer formatting
        if len(message) > 200:
            payload = {
                "username": "🔒 SSL Monitor",
                "attachments": [{
                    "fallback": message,
                    "text": message,
                    "color": "#6366f1",
                    "mattermost_app_id": "ssl-checker"
                }]
            }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=payload, timeout=10) as resp:
                if resp.status not in [200, 201]:
                    logger.warning(f"Mattermost webhook returned {resp.status}")
    except Exception as e: 
        logger.error(f"Mattermost Error: {e}")

async def send_slack(message: str, webhook_url: str):
    if not webhook_url: return
    try:
        payload = {"text": message}
        async with aiohttp.ClientSession() as session:
            await session.post(webhook_url, json=payload, timeout=10)
    except Exception as e: logger.error(f"Slack Error: {e}")

async def send_custom_webhook(message: str, webhook_url: str):
    if not webhook_url: return
    try:
        payload = {"content": message, "title": "SSL Monitor Alert", "source": "ssl-checker"}
        async with aiohttp.ClientSession() as session:
            await session.post(webhook_url, json=payload, timeout=10)
    except Exception as e: logger.error(f"Custom Webhook Error: {e}")

# --- Test Functions ---
async def send_test_telegram_msg(token: str, chat_id: str, proxy: str = None) -> dict:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id, 
        "text": "✅ **SSL Monitor Test**\n\nTelegram connection is working!\nThis message confirms that your bot can send messages to this chat/group.", 
        "parse_mode": "Markdown"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, proxy=proxy, timeout=10) as resp:
                return {"success": True} if resp.status == 200 else {"success": False, "error": await resp.text()}
    except Exception as e: return {"success": False, "error": str(e)}

async def send_test_mattermost_msg(webhook_url: str) -> dict:
    if not webhook_url: return {"success": False, "error": "URL is empty"}
    
    # Test payload with emoji icon (more reliable than icon_url)
    payload = {
        "text": "✅ **SSL Monitor Test**\nMattermost integration is working!",
        "username": "🔒 SSL Monitor",
        "icon_emoji": ":lock:"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=payload, timeout=10) as resp:
                if resp.status in [200, 201]:
                    return {"success": True}
                else:
                    error_text = await resp.text()
                    return {"success": False, "error": f"Status {resp.status}: {error_text}"}
    except Exception as e: 
        return {"success": False, "error": str(e)}

async def send_test_webhook_msg(webhook_url: str, platform: str) -> dict:
    if not webhook_url: return {"success": False, "error": "URL is empty"}
    
    payload = {}
    if platform == 'slack': payload = {"text": "✅ **SSL Monitor Test**\nSlack connected!"}
    else: payload = {"content": "✅ **SSL Monitor Test**\nCustom Webhook connected!", "title": "Test"}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=payload, timeout=10) as resp:
                return {"success": True} if resp.status in [200, 201, 204] else {"success": False, "error": f"Status {resp.status}"}
    except Exception as e: return {"success": False, "error": str(e)}

# --- Main Notify Function ---
async def notify_all(message: str, settings: AppSettings):
    if settings:
        await send_telegram(message, settings)
        if settings.mattermost_url: await send_mattermost(message, settings.mattermost_url)
        if settings.slack_webhook_url: await send_slack(message, settings.slack_webhook_url)
        if settings.custom_webhook_url: await send_custom_webhook(message, settings.custom_webhook_url)