import ssl
import socket
import datetime
import whois
import asyncio
import re
import logging
import urllib.request
import json

logger = logging.getLogger(__name__)

# --- Helper: Create Unsafe Context (For Mac SSL Issues) ---
def get_unsafe_context():
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx
    except:
        return None

# --- Helper: Clean Domain Name ---
def clean_domain(hostname: str) -> str:
    if not hostname: return ""
    # Remove protocol
    hostname = hostname.replace("https://", "").replace("http://", "")
    # Remove path
    hostname = hostname.split("/")[0]
    # Remove www. (optional but often good for whois)
    hostname = hostname.replace("www.", "")
    # Remove whitespace
    return hostname.strip()

# --- 1. Check SSL ---
def get_ssl_expiry_sync(hostname: str):
    # Clean the hostname before connecting
    hostname = clean_domain(hostname)
    if not hostname: return None

    try:
        # SSL context must be standard for verification
        context = ssl.create_default_context()
        # Reduced timeout to fail fast if domain is unreachable
        with socket.create_connection((hostname, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as sslsock:
                cert = sslsock.getpeercert()
                return datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
    except socket.gaierror:
        # DNS Error [Errno 8]
        logger.warning(f"DNS lookup failed for {hostname}")
        return None
    except Exception as e:
        # logger.debug(f"SSL Check Error for {hostname}: {e}")
        return None

# --- 2. Check Domain (API Based) ---
def get_whois_api(hostname: str):
    """Use API for domains where direct Whois is blocked"""
    hostname = clean_domain(hostname)
    if not hostname: return None

    # List of free APIs
    apis = [
        f"[https://api.hackertarget.com/whois/?q=](https://api.hackertarget.com/whois/?q=){hostname}",
        f"[https://www.whois.com/whois/](https://www.whois.com/whois/){hostname}"
    ]
    
    for url in apis:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            # Use unsafe context to avoid Mac SSL errors
            with urllib.request.urlopen(req, timeout=10, context=get_unsafe_context()) as response:
                text = response.read().decode('utf-8', errors='ignore')
                
                # Patterns for expiry date
                patterns = [
                    r'expire-date:\s*(\d{4}-\d{2}-\d{2})',       # irnic
                    r'Registry Expiry Date:\s*(\d{4}-\d{2}-\d{2})',
                    r'Expiry Date:\s*(\d{4}-\d{2}-\d{2})',
                    r'Expires On:</div><div class="df-value">(\d{4}-\d{2}-\d{2})</div>'
                ]
                
                for p in patterns:
                    match = re.search(p, text, re.IGNORECASE)
                    if match:
                        return datetime.datetime.strptime(match.group(1), '%Y-%m-%d')
        except:
            continue
    return None

def get_domain_expiry_sync(hostname: str):
    hostname = clean_domain(hostname)
    if not hostname: return None

    # Priority 1: Standard Library
    try:
        w = whois.whois(hostname)
        if w.expiration_date:
            exp = w.expiration_date
            if isinstance(exp, list): return exp[0]
            if isinstance(exp, datetime.datetime): return exp
    except:
        pass

    # Priority 2: API Fallback
    return get_whois_api(hostname)

async def check_domain_data(hostname: str):
    # Run concurrently
    ssl_date = await asyncio.to_thread(get_ssl_expiry_sync, hostname)
    domain_date = await asyncio.to_thread(get_domain_expiry_sync, hostname)
    return ssl_date, domain_date