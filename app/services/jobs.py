import logging
import asyncio
import datetime
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.all_models import Domain, AppSettings, DomainHistory
from app.services.checker import check_domain_data, get_ssl_expiry_sync, get_domain_expiry_sync
from app.services.notifier import notify_all

logger = logging.getLogger(__name__)

async def process_single_domain(domain_obj, today, db: Session):
    domain_url = domain_obj.url
    settings = db.query(AppSettings).first()
    
    # 1. انجام چک‌ها بر اساس تنظیمات کاربر
    ssl_exp = None
    dom_exp = None
    
    # فقط اگر کاربر خواسته باشد چک می‌کنیم
    if domain_obj.monitor_ssl:
        ssl_exp = await asyncio.to_thread(get_ssl_expiry_sync, domain_url)
        
    if domain_obj.monitor_domain:
        dom_exp = await asyncio.to_thread(get_domain_expiry_sync, domain_url)

    # تعیین حدود
    s_danger = domain_obj.custom_ssl_danger or (settings.ssl_danger_days if settings else 7)
    s_warning = domain_obj.custom_ssl_warning or (settings.ssl_warning_days if settings else 30)
    d_danger = domain_obj.custom_domain_danger or (settings.domain_danger_days if settings else 14)
    d_warning = domain_obj.custom_domain_warning or (settings.domain_warning_days if settings else 60)

    # دریافت قالب‌های پیام (یا پیش‌فرض)
    tpl_ssl_warn = settings.msg_ssl_warning if settings and settings.msg_ssl_warning else "⚠️ SSL Warning: {url} ({days} days)"
    tpl_ssl_crit = settings.msg_ssl_danger if settings and settings.msg_ssl_danger else "🚨 SSL Critical: {url} ({days} days)"
    tpl_dom_warn = settings.msg_dom_warning if settings and settings.msg_dom_warning else "⏳ Domain Warning: {url} ({days} days)"
    tpl_dom_crit = settings.msg_dom_danger if settings and settings.msg_dom_danger else "🔥 Domain Critical: {url} ({days} days)"

    msg = ""
    status = "valid"
    should_notify = False
    
    # --- منطق SSL ---
    ssl_days = None
    if domain_obj.monitor_ssl:
        if ssl_exp:
            ssl_days = (ssl_exp - today).days
            if ssl_days <= s_danger:
                msg += tpl_ssl_crit.format(url=domain_url, days=ssl_days) + "\n"
                status = "expired"
                if domain_obj.notify_critical: should_notify = True
            elif ssl_days <= s_warning:
                msg += tpl_ssl_warn.format(url=domain_url, days=ssl_days) + "\n"
                if status != "expired": status = "warning"
                if domain_obj.notify_warning: should_notify = True
    
    # --- منطق Domain ---
    dom_days = None
    if domain_obj.monitor_domain:
        if dom_exp:
            dom_days = (dom_exp - today).days
            if dom_days <= d_danger:
                msg += tpl_dom_crit.format(url=domain_url, days=dom_days) + "\n"
                status = "expired"
                if domain_obj.notify_critical: should_notify = True
            elif dom_days <= d_warning:
                msg += tpl_dom_warn.format(url=domain_url, days=dom_days) + "\n"
                if status != "expired": status = "warning"
                if domain_obj.notify_warning: should_notify = True
    
    if msg and should_notify and settings:
        await notify_all(msg, settings)

    try:
        history = DomainHistory(
            domain_id=domain_obj.id,
            ssl_days=ssl_days,
            domain_days=dom_days,
            overall_status=status,
            checked_at=today
        )
        db.add(history)
    except Exception as e:
        logger.error(f"Error saving history: {e}")

async def check_job():
    logger.info("Starting background check...")
    today = datetime.datetime.now()
    db = SessionLocal()
    try:
        domains = db.query(Domain).all()
        if domains:
            tasks = [process_single_domain(d, today, db) for d in domains]
            await asyncio.gather(*tasks)
            db.commit()
    except Exception as e:
        logger.error(f"Job Error: {e}")
        db.rollback()
    finally:
        db.close()
    logger.info("Check finished.")