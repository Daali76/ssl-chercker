import ssl
import socket
import datetime
import whois
import asyncio
import logging

# تنظیم لاگر
logger = logging.getLogger(__name__)

def get_ssl_expiry_sync(hostname: str):
    """
    بررسی گواهی SSL (استاندارد و دقیق)
    """
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as sslsock:
                cert = sslsock.getpeercert()
                return datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
    except Exception as e:
        # خطا را چاپ نمی‌کنیم تا لاگ شلوغ نشود، فقط در صورت نیاز
        return None

def get_domain_expiry_sync(hostname: str):
    """
    بررسی دامنه با استفاده از کتابخانه استاندارد
    اگر کار کرد که عالی، اگر نه (مثل ir در شبکه شما) نادیده می‌گیرد.
    """
    try:
        w = whois.whois(hostname)
        
        # استخراج تاریخ انقضا
        exp = w.expiration_date
        
        # هندل کردن حالت‌هایی که خروجی لیست است
        if isinstance(exp, list):
            return exp[0]
        
        if isinstance(exp, datetime.datetime):
            return exp
            
    except Exception:
        # اگر به هر دلیلی (تحریم، DNS، فیلتر) نشد، بیخیال می‌شود
        return None
    
    return None

async def check_domain_data(hostname: str):
    # اجرای همزمان SSL و Domain
    ssl_date = await asyncio.to_thread(get_ssl_expiry_sync, hostname)
    domain_date = await asyncio.to_thread(get_domain_expiry_sync, hostname)
    return ssl_date, domain_date