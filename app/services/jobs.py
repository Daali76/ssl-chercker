import logging
import asyncio
import datetime
from app.db.session import SessionLocal
from app.models.all_models import Domain
from app.services.checker import check_domain_data
from app.services.notifier import notify_all
from app.core.config import settings

async def process_single_domain(domain, today):
    ssl_exp, dom_exp = await check_domain_data(domain)
    
    msg = ""
    # Check SSL
    if ssl_exp:
        days = (ssl_exp - today).days
        if days < 3: msg += f"🚨 **SSL EXPIRED!** {domain}\n"
        elif days < settings.EXPIRY_THRESHOLD_DAYS: msg += f"⚠️ **SSL Expiring** {domain}: {days} days\n"
    
    # Check Domain
    if dom_exp:
        dom_days = (dom_exp - today).days
        if dom_days < 7: msg += f"🔥 **DOMAIN EXPIRED SOON!** {domain}: {dom_days} days\n"
    
    if msg: await notify_all(msg)

async def check_job():
    logging.info("Starting background check...")
    today = datetime.datetime.now()
    
    db = SessionLocal()
    domains = db.query(Domain).all()
    db.close()
    
    if not domains: return

    tasks = []
    for d in domains:
        tasks.append(process_single_domain(d.url, today))
    await asyncio.gather(*tasks)
    logging.info("Background check finished.")