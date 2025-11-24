import asyncio
import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.all_models import User, Domain, AppSettings
from app.schemas.schemas import SettingsUpdate
from app.core.security import get_current_user, get_current_admin
from app.core.config import settings
from app.services.checker import check_domain_data
from app.services.jobs import check_job

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
    # --- FIX: جلوگیری از کش شدن صفحه ادمین ---
    # این هدرها مرورگر را مجبور می‌کنند همیشه نسخه جدید فایل را بگیرد
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
    
    # دریافت مقادیر پیش‌فرض از تنظیمات
    g_s_danger = app_settings.ssl_danger_days if app_settings else 7
    g_s_warning = app_settings.ssl_warning_days if app_settings else 30
    g_d_danger = app_settings.domain_danger_days if app_settings else 14
    g_d_warning = app_settings.domain_warning_days if app_settings else 60

    if not domains:
        return {"domains": [], "check_time": today.strftime('%Y-%m-%d %H:%M:%S'), "is_admin": user.role == "admin"}

    async def get_data(d):
        ssl_exp, dom_exp = await check_domain_data(d.url)
        
        # --- تعیین حد مجاز (اختصاصی دامنه یا کلی) ---
        s_danger = d.custom_ssl_danger if d.custom_ssl_danger is not None else g_s_danger
        s_warning = d.custom_ssl_warning if d.custom_ssl_warning is not None else g_s_warning
        
        d_danger = d.custom_domain_danger if d.custom_domain_danger is not None else g_d_danger
        d_warning = d.custom_domain_warning if d.custom_domain_warning is not None else g_d_warning

        # --- محاسبه وضعیت SSL ---
        ssl_days = (ssl_exp - today).days if ssl_exp else None
        ssl_status = "error"
        if ssl_days is not None:
            if ssl_days <= s_danger: ssl_status = "expired"     # قرمز
            elif ssl_days <= s_warning: ssl_status = "warning"  # زرد
            else: ssl_status = "valid"                          # سبز
            
        # --- محاسبه وضعیت Domain ---
        dom_days = (dom_exp - today).days if dom_exp else None
        dom_status = "error"
        if dom_days is not None:
            if dom_days <= d_danger: dom_status = "expired"
            elif dom_days <= d_warning: dom_status = "warning"
            else: dom_status = "valid"

        # Overall Status (بدترین وضعیت را انتخاب می‌کند)
        overall_status = "valid"
        if ssl_status == "error" or dom_status == "error": overall_status = "error"
        elif ssl_status == "expired" or dom_status == "expired": overall_status = "expired"
        elif ssl_status == "warning" or dom_status == "warning": overall_status = "warning"

        return {
            "domain": d.url,
            "overall_status": overall_status,
            "ssl": {
                "expiry_date": ssl_exp.strftime('%Y-%m-%d') if ssl_exp else None,
                "days_remaining": ssl_days,
                "status": ssl_status,
                "message": f"{ssl_days} days" if ssl_days is not None else "Error"
            },
            "domain_registration": {
                "expiry_date": dom_exp.strftime('%Y-%m-%d') if dom_exp else None,
                "days_remaining": dom_days,
                "status": dom_status,
                "message": f"{dom_days} days" if dom_days is not None else "Hidden/Error"
            }
        }

    results = await asyncio.gather(*[get_data(d) for d in domains])
    return {
        "domains": results,
        "check_time": today.strftime('%Y-%m-%d %H:%M:%S'),
        "is_admin": user.role == "admin"
    }

@router.get("/check-now")
async def trigger_check(user: User = Depends(get_current_user)):
    asyncio.create_task(check_job())
    return {"status": "started"}

# --- Settings APIs ---
@router.get("/settings")
def get_app_settings(admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return db.query(AppSettings).first()

@router.put("/settings")
def update_app_settings(data: SettingsUpdate, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    s = db.query(AppSettings).first()
    
    # آپدیت تنظیمات شبکه
    if data.telegram_bot_token is not None: s.telegram_bot_token = data.telegram_bot_token
    if data.telegram_chat_id is not None: s.telegram_chat_id = data.telegram_chat_id
    if data.proxy_url is not None: s.proxy_url = data.proxy_url
    if data.mattermost_url is not None: s.mattermost_url = data.mattermost_url
    
    # آپدیت تنظیمات رنگ‌بندی (Global Thresholds)
    if data.ssl_danger_days is not None: s.ssl_danger_days = data.ssl_danger_days
    if data.ssl_warning_days is not None: s.ssl_warning_days = data.ssl_warning_days
    if data.domain_danger_days is not None: s.domain_danger_days = data.domain_danger_days
    if data.domain_warning_days is not None: s.domain_warning_days = data.domain_warning_days
    
    db.commit()
    return {"status": "updated"}