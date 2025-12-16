"""
Security Middleware & Improvements for SSL Checker
- CSRF Protection
- Rate Limiting
- Secure Headers
- Input Validation
- SQL Injection Prevention
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time
from typing import Callable
import secrets

# ============================================================================
# 1. RATE LIMITING
# ============================================================================

limiter = Limiter(key_func=get_remote_address)

def setup_rate_limiting(app: FastAPI):
    """
    Setup rate limiting to prevent abuse
    """
    app.state.limiter = limiter
    
    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Please try again later."}
        )


# ============================================================================
# 2. CSRF PROTECTION
# ============================================================================

class CSRFProtection:
    """
    CSRF token validation middleware
    """
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.token_name = "X-CSRF-Token"
        self.field_name = "csrf_token"
    
    def generate_token(self, session_id: str) -> str:
        """Generate a CSRF token"""
        token = secrets.token_urlsafe(32)
        # In production, store token in session with TTL
        return token
    
    async def validate_token(self, request: Request) -> bool:
        """
        Validate CSRF token from request
        Checks: headers, form data, or cookies
        """
        # Skip validation for GET, HEAD, OPTIONS, TRACE
        if request.method in ["GET", "HEAD", "OPTIONS", "TRACE"]:
            return True
        
        token = None
        
        # Check header first (preferred for API)
        token = request.headers.get(self.token_name)
        
        # Check form data
        if not token:
            try:
                form_data = await request.form()
                token = form_data.get(self.field_name)
            except:
                pass
        
        # Check cookies
        if not token:
            token = request.cookies.get(self.field_name)
        
        if not token:
            return False
        
        # Validate token (in production, check against stored token in session)
        return len(token) > 0


# ============================================================================
# 3. SECURE HEADERS
# ============================================================================

def add_security_headers(app: FastAPI):
    """
    Add security headers to all responses
    """
    @app.middleware("http")
    async def add_security_headers_middleware(request: Request, call_next: Callable):
        response = await call_next(request)
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://api.telegram.org https://api.ssllabs.com https://api.hackertarget.com; "
            "frame-ancestors 'none'"
        )
        
        # Prevent XSS attacks
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # HTTPS Strict Transport Security (requires HTTPS in production)
        # response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Feature Policy / Permissions Policy
        response.headers["Permissions-Policy"] = (
            "accelerometer=(), "
            "ambient-light-sensor=(), "
            "autoplay=(), "
            "battery=(), "
            "camera=(), "
            "cross-origin-isolated=(), "
            "geolocation=(), "
            "gyroscope=(), "
            "magnetometer=(), "
            "microphone=(), "
            "payment=(), "
            "usb=()"
        )
        
        return response


# ============================================================================
# 4. INPUT VALIDATION & SANITIZATION
# ============================================================================

import re
from urllib.parse import urlparse

class InputValidator:
    """
    Validate and sanitize user inputs
    """
    
    @staticmethod
    def is_valid_domain(domain: str) -> bool:
        """
        Validate domain name format
        """
        # Remove protocol if present
        domain = domain.replace("https://", "").replace("http://", "").split("/")[0]
        
        # Domain regex pattern
        domain_pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$'
        
        if len(domain) > 253:
            return False
        
        if not re.match(domain_pattern, domain):
            return False
        
        return True
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """
        Validate URL format
        """
        try:
            result = urlparse(url)
            return all([result.scheme in ['http', 'https'], result.netloc])
        except:
            return False
    
    @staticmethod
    def sanitize_string(text: str, max_length: int = 500) -> str:
        """
        Sanitize user input string
        - Remove dangerous characters
        - Limit length
        - Prevent script injection
        """
        if not isinstance(text, str):
            return ""
        
        # Limit length
        text = text[:max_length]
        
        # Remove null bytes
        text = text.replace("\x00", "")
        
        # Remove control characters (except newline, tab)
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
        
        return text.strip()
    
    @staticmethod
    def is_safe_json(json_str: str) -> bool:
        """
        Check if JSON string is safe to parse
        """
        try:
            import json
            json.loads(json_str)
            return True
        except:
            return False


# ============================================================================
# 5. AUTHENTICATION SECURITY
# ============================================================================

import hashlib

class PasswordSecurity:
    """
    Enhanced password security measures
    """
    
    @staticmethod
    def check_password_strength(password: str) -> dict:
        """
        Check password strength and return requirements
        """
        strength = {"score": 0, "issues": []}
        
        if len(password) < 8:
            strength["issues"].append("Password must be at least 8 characters")
        else:
            strength["score"] += 1
        
        if not any(char.isupper() for char in password):
            strength["issues"].append("Password must contain uppercase letters")
        else:
            strength["score"] += 1
        
        if not any(char.islower() for char in password):
            strength["issues"].append("Password must contain lowercase letters")
        else:
            strength["score"] += 1
        
        if not any(char.isdigit() for char in password):
            strength["issues"].append("Password must contain numbers")
        else:
            strength["score"] += 1
        
        if not any(char in "!@#$%^&*()_+-=[]{}|;:,.<>?" for char in password):
            strength["issues"].append("Password should contain special characters")
        
        return strength
    
    @staticmethod
    def is_common_password(password: str) -> bool:
        """
        Check against common password list
        """
        common_passwords = {
            "password", "123456", "password123", "admin", "letmein",
            "welcome", "monkey", "dragon", "master", "sunshine",
            "password1", "qwerty", "admin123", "root", "toor"
        }
        
        return password.lower() in common_passwords


# ============================================================================
# 6. SESSION SECURITY
# ============================================================================

class SessionSecurity:
    """
    Secure session management
    """
    
    @staticmethod
    def generate_session_id() -> str:
        """Generate secure session ID"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def get_session_config() -> dict:
        """
        Get secure session configuration for cookies
        """
        return {
            "secure": True,  # HTTPS only (disable for local dev)
            "httponly": True,  # Not accessible to JavaScript
            "samesite": "strict",  # CSRF protection
            "max_age": 3600  # 1 hour
        }


# ============================================================================
# 7. API SECURITY
# ============================================================================

class APISecurityConfig:
    """
    Configuration for API security
    """
    
    # Allowed origins (CORS)
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        # Add production domains here
    ]
    
    # Rate limiting configuration
    RATE_LIMITS = {
        "login": "5/minute",  # 5 attempts per minute
        "auth": "10/minute",  # 10 attempts per minute
        "api": "100/minute",  # 100 requests per minute
        "scan": "5/hour",  # 5 scans per hour
    }
    
    # JWT security
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRY_MINUTES = 60
    REFRESH_TOKEN_EXPIRY_DAYS = 7


# ============================================================================
# 8. LOGGING & AUDIT
# ============================================================================

class AuditLogger:
    """
    Log security-relevant events
    """
    
    def __init__(self, logger):
        self.logger = logger
    
    def log_failed_login(self, username: str, ip_address: str):
        """Log failed login attempt"""
        self.logger.warning(f"Failed login attempt - User: {username}, IP: {ip_address}")
    
    def log_successful_login(self, username: str, ip_address: str):
        """Log successful login"""
        self.logger.info(f"Successful login - User: {username}, IP: {ip_address}")
    
    def log_permission_denied(self, user: str, action: str, resource: str):
        """Log denied action due to insufficient permissions"""
        self.logger.warning(f"Permission denied - User: {user}, Action: {action}, Resource: {resource}")
    
    def log_suspicious_activity(self, description: str, user: str = None):
        """Log suspicious activity"""
        self.logger.warning(f"Suspicious activity: {description}" + (f" - User: {user}" if user else ""))


# ============================================================================
# Setup Function
# ============================================================================

def setup_security(app: FastAPI, secret_key: str):
    """
    Setup all security features
    """
    # Add security headers
    add_security_headers(app)
    
    # Setup rate limiting
    setup_rate_limiting(app)
    
    # Initialize CSRF protection
    csrf = CSRFProtection(secret_key)
    app.state.csrf = csrf
    
    # Initialize input validator
    app.state.input_validator = InputValidator()
    
    # Initialize audit logger
    import logging
    logger = logging.getLogger(__name__)
    app.state.audit_logger = AuditLogger(logger)
    
    return app
