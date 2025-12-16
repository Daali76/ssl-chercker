import asyncio
import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.all_models import User, Domain, AppSettings
from app.schemas.schemas import SettingsUpdate, TelegramTestRequest, WebhookTestRequest, MattermostTestRequest
from app.core.security import get_current_user, get_current_admin
from app.services.checker import check_domain_data
from app.services.jobs import check_job
from app.services.notifier import send_test_telegram_msg, send_test_webhook_msg, notify_all, send_test_mattermost_msg

router = APIRouter()

# --- HTML Pages ---
@router.get("/")
def read_root(): return FileResponse("static/dashboard.html")

@router.get("/login")
def login_page(): return FileResponse("static/login.html")

@router.get("/dashboard")
def dashboard_page(): return FileResponse("static/dashboard.html")

@router.get("/admin")
def admin_page():
    response = FileResponse("static/admin.html")
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# --- Dashboard APIs ---
@router.get("/ssl-status")
async def get_ssl_status(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    today = datetime.datetime.now()
    domains = db.query(Domain).all()
    app_settings = db.query(AppSettings).first()
    
    # Default values
    g_s_danger = app_settings.ssl_danger_days if app_settings else 7
    g_s_warning = app_settings.ssl_warning_days if app_settings else 30
    g_d_danger = app_settings.domain_danger_days if app_settings else 14
    g_d_warning = app_settings.domain_warning_days if app_settings else 60

    if not domains:
        return {"domains": [], "check_time": today.strftime('%Y-%m-%d %H:%M:%S'), "is_admin": user.role == "admin"}

    async def get_data(d):
        # Get raw data
        raw_ssl, raw_dom = await check_domain_data(d.url)
        
        # Apply monitoring filter
        ssl_exp = raw_ssl if d.monitor_ssl else None
        dom_exp = raw_dom if d.monitor_domain else None

        # Thresholds
        s_danger = d.custom_ssl_danger if d.custom_ssl_danger is not None else g_s_danger
        s_warning = d.custom_ssl_warning if d.custom_ssl_warning is not None else g_s_warning
        d_danger = d.custom_domain_danger if d.custom_domain_danger is not None else g_d_danger
        d_warning = d.custom_domain_warning if d.custom_domain_warning is not None else g_d_warning

        # SSL Status
        ssl_days = (ssl_exp - today).days if ssl_exp else None
        ssl_status = "error"
        if ssl_days is not None:
            if ssl_days <= s_danger: ssl_status = "expired"
            elif ssl_days <= s_warning: ssl_status = "warning"
            else: ssl_status = "valid"
        elif not d.monitor_ssl:
             ssl_status = "disabled"
            
        # Domain Status
        dom_days = (dom_exp - today).days if dom_exp else None
        dom_status = "error"
        if dom_days is not None:
            if dom_days <= d_danger: dom_status = "expired"
            elif dom_days <= d_warning: dom_status = "warning"
            else: dom_status = "valid"
        elif not d.monitor_domain:
            dom_status = "disabled"

        # Overall Status
        overall_status = "valid"
        states = []
        if d.monitor_ssl: states.append(ssl_status)
        if d.monitor_domain: states.append(dom_status)
        
        if "expired" in states: overall_status = "expired"
        elif "warning" in states: overall_status = "warning"
        elif "error" in states: overall_status = "error"
        
        return {
            "id": d.id,
            "domain": d.url,
            "overall_status": overall_status,
            "ssl": { "expiry_date": ssl_exp.strftime('%Y-%m-%d') if ssl_exp else None, "days_remaining": ssl_days, "status": ssl_status },
            "domain_registration": { "expiry_date": dom_exp.strftime('%Y-%m-%d') if dom_exp else None, "days_remaining": dom_days, "status": dom_status }
        }

    results = await asyncio.gather(*[get_data(d) for d in domains])
    return { "domains": results, "check_time": today.strftime('%Y-%m-%d %H:%M:%S'), "is_admin": user.role == "admin" }

@router.get("/check-now")
async def trigger_check(user: User = Depends(get_current_user)):
    asyncio.create_task(check_job())
    return {"status": "started"}

# --- Settings & Test APIs ---
@router.get("/settings")
def get_app_settings(admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return db.query(AppSettings).first()

@router.put("/settings")
def update_app_settings(data: SettingsUpdate, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    s = db.query(AppSettings).first()
    
    # Network & Notification
    if data.telegram_bot_token is not None: s.telegram_bot_token = data.telegram_bot_token
    if data.telegram_chat_id is not None: s.telegram_chat_id = data.telegram_chat_id
    if data.proxy_url is not None: s.proxy_url = data.proxy_url
    if data.mattermost_url is not None: s.mattermost_url = data.mattermost_url
    if data.slack_webhook_url is not None: s.slack_webhook_url = data.slack_webhook_url
    if data.custom_webhook_url is not None: s.custom_webhook_url = data.custom_webhook_url
    
    # Colors & Interval
    if data.ssl_danger_days is not None: s.ssl_danger_days = data.ssl_danger_days
    if data.ssl_warning_days is not None: s.ssl_warning_days = data.ssl_warning_days
    if data.domain_danger_days is not None: s.domain_danger_days = data.domain_danger_days
    if data.domain_warning_days is not None: s.domain_warning_days = data.domain_warning_days
    if data.check_interval_hours is not None: s.check_interval_hours = data.check_interval_hours
    
    # Messages
    if data.msg_ssl_warning is not None: s.msg_ssl_warning = data.msg_ssl_warning
    if data.msg_ssl_danger is not None: s.msg_ssl_danger = data.msg_ssl_danger
    if data.msg_dom_warning is not None: s.msg_dom_warning = data.msg_dom_warning
    if data.msg_dom_danger is not None: s.msg_dom_danger = data.msg_dom_danger
    
    db.commit()
    return {"status": "updated"}

# --- Tests ---
@router.post("/settings/test-telegram")
async def test_telegram_connection(req: TelegramTestRequest, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    settings = db.query(AppSettings).first()
    proxy = settings.proxy_url if settings else None
    result = await send_test_telegram_msg(req.token, req.chat_id, proxy)
    if result["success"]: return {"status": "ok", "message": "Telegram OK"}
    else: raise HTTPException(status_code=400, detail=f"Failed: {result.get('error')}")

@router.post("/settings/test-mattermost")
async def test_mattermost_connection(req: MattermostTestRequest, admin: User = Depends(get_current_admin)):
    result = await send_test_mattermost_msg(req.webhook_url)
    if result["success"]: return {"status": "ok", "message": "Mattermost OK"}
    else: raise HTTPException(status_code=400, detail=f"Failed: {result.get('error')}")

@router.post("/settings/test-webhook")
async def test_webhook_connection(req: WebhookTestRequest, platform: str = 'custom', admin: User = Depends(get_current_admin)):
    result = await send_test_webhook_msg(req.webhook_url, platform)
    if result["success"]: return {"status": "ok", "message": f"{platform.title()} OK"}
    else: raise HTTPException(status_code=400, detail=f"Failed: {result.get('error')}")

@router.post("/settings/test-alert")
async def test_critical_alert(admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    settings = db.query(AppSettings).first()
    msg = "🚨 **SSL CRITICAL**: simulation.com\nExpires in: -1 days\n*(Test Alert)*"
    await notify_all(msg, settings)
    return {"status": "ok", "message": "Simulation sent!"}