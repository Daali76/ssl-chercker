# 🔒 SSL & Domain Checker

A modern, production-ready FastAPI application for monitoring SSL certificates, domain expiration, and security vulnerabilities with real-time notifications and comprehensive vulnerability scanning.

**Status**: ✅ Production Ready | v2.0.0 | All security features included | Fully tested and documented

---

## 🎯 Features

### Core Monitoring
- ✅ **SSL Certificate Monitoring** - Track expiration dates and get alerts
- ✅ **Domain Expiration Tracking** - Monitor domain registration expiry
- ✅ **Vulnerability Scanning** - Detect open ports, weak SSL/TLS, missing headers
- ✅ **Security Headers Audit** - Verify HSTS, CSP, X-Frame-Options, etc.
- ✅ **DNS Security Check** - Validate SPF, DMARC, MX records

### Notifications
- 📱 **Telegram** - Direct bot notifications
- 💬 **Mattermost** - Team chat integration (fixed in v2.0)
- 📡 **Slack** - Webhook support
- 🔗 **Custom Webhooks** - Custom integration support

### Security
- 🔐 **CSRF Protection** - Token-based CSRF defense
- ⏱️ **Rate Limiting** - Prevent brute force and abuse
- 🛡️ **Secure Headers** - CSP, HSTS, X-Frame-Options, etc.
- ✅ **Input Validation** - SQL injection and XSS prevention
- 👤 **Role-Based Access** - Admin and User roles
- 📋 **Audit Logging** - Track all security events

### User Management
- 👥 Multi-user support
- 🔑 JWT authentication
- 👨‍💼 Admin and regular user roles
- ⚙️ Configurable settings per user

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
docker-compose up -d

# Access: http://localhost:8000
# Default credentials:
#   Username: admin
#   Password: admin
```

### Option 2: Local Development

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup PostgreSQL (see LOCAL_SETUP.md)
python main.py

# Access: http://localhost:8000
```

---

## 📚 Documentation

### Getting Started
- **[INSTALLATION.md](./INSTALLATION.md)** - Step-by-step installation guide
- **[LOCAL_SETUP.md](./LOCAL_SETUP.md)** - PostgreSQL setup for development

### Features & Usage
- **[FEATURES_SECURITY.md](./FEATURES_SECURITY.md)** - Complete feature documentation
  - Vulnerability scanning API
  - Mattermost integration (fixed!)
  - Security features explained
  - Usage examples with cURL and JavaScript

### Deployment
- **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** - Production deployment options
  - Docker deployment
  - Linux server setup (Ubuntu/Debian)
  - Cloud platforms (AWS, Heroku, DigitalOcean)
  - SSL/TLS configuration
  - Monitoring and backups

### Help & Troubleshooting
- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - Common issues and solutions
- **[API Documentation](http://localhost:8000/docs)** - Interactive Swagger UI (when running)

---

## 🔍 Vulnerability Scanning

Comprehensive security scanning for domains:

```bash
# Scan a domain for vulnerabilities
curl -X POST http://localhost:8000/api/vulnerabilities/scan/1 \
  -H "Authorization: Bearer $TOKEN"

# Get formatted report
curl http://localhost:8000/api/vulnerabilities/report/1 \
  -H "Authorization: Bearer $TOKEN"
```

**Scan Results Include**:
- Open ports detection
- SSL/TLS configuration analysis
- Security headers audit
- DNS security validation
- Overall risk assessment (CRITICAL → MINIMAL)

---

## ⚙️ Configuration

### Environment Variables

Create `.env` file (copy from `.env.example`):

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/sslchecker

# Security
SECRET_KEY=your-secret-key-here

# Notifications
TELEGRAM_BOT_TOKEN=xxx
TELEGRAM_CHAT_ID=xxx
MATTERMOST_URL=https://your-mattermost.com/hooks/xxx

# Monitoring
CHECK_INTERVAL_HOURS=24
SSL_WARNING_DAYS=30
SSL_DANGER_DAYS=7
DOMAIN_WARNING_DAYS=60
DOMAIN_DANGER_DAYS=14

# Logging
LOG_LEVEL=INFO
```

### First Time Setup

After starting the application:

1. **Login** with default credentials
   - Username: `admin`
   - Password: `admin`

2. **Change Admin Password** - Go to Settings → User Profile

3. **Configure Notifications**
   - Telegram: Add bot token and chat ID
   - Mattermost: Add webhook URL and test
   - Slack: Add webhook URL

4. **Add Domains** - Click "Add Domain" on dashboard

5. **Configure Thresholds** - Set SSL and domain expiration alerts

---

## 📊 Project Structure

```
ssl-checker/
├── app/
│   ├── core/              # Configuration & security
│   │   ├── config.py      # Settings management
│   │   ├── security.py    # Authentication & JWT
│   │   └── security_middleware.py  # NEW: CSRF, rate limiting, etc.
│   ├── db/                # Database layer
│   │   └── session.py     # SQLAlchemy setup
│   ├── models/            # Data models
│   │   └── all_models.py
│   ├── routers/           # API endpoints
│   │   ├── auth.py        # Authentication
│   │   ├── users.py       # User management
│   │   ├── domains.py     # Domain CRUD
│   │   ├── dashboard.py   # Dashboard data
│   │   └── vulnerabilities.py  # NEW: Vulnerability scanning
│   ├── services/          # Business logic
│   │   ├── checker.py     # SSL/domain checking
│   │   ├── jobs.py        # Scheduled jobs
│   │   ├── notifier.py    # Notifications (Mattermost fixed!)
│   │   └── vulnerability_scanner.py  # NEW: Vulnerability scanning
│   └── schemas/           # Request/response schemas
│       └── schemas.py
├── static/                # Frontend
│   ├── login.html
│   ├── dashboard.html
│   └── admin.html
├── scripts/               # Utility scripts
│   ├── reset_db.py
│   └── debug_ir.py
├── main.py                # FastAPI application
├── requirements.txt       # Python dependencies
├── docker-compose.yml     # Docker Compose config
├── Dockerfile             # Docker image
└── README.md             # This file
```

---

## 🛠️ API Endpoints

### Authentication
- `POST /auth/login` - Login with credentials
- `POST /auth/refresh` - Refresh JWT token

### Domains
- `GET /domains` - List all domains
- `POST /domains` - Add new domain
- `GET /domains/{id}` - Get domain details
- `PUT /domains/{id}` - Update domain
- `DELETE /domains/{id}` - Delete domain

### Vulnerabilities (NEW in v2.0)
- `POST /api/vulnerabilities/scan/{domain_id}` - Scan domain
- `GET /api/vulnerabilities/scan/{domain_id}` - Get scan results
- `POST /api/vulnerabilities/scan-all` - Scan all domains
- `GET /api/vulnerabilities/report/{domain_id}` - Get report

### Dashboard
- `GET /dashboard` - Dashboard data
- `POST /dashboard/check-now` - Trigger manual check

### Admin
- `GET /admin` - Admin settings
- `POST /admin/test-telegram` - Test Telegram
- `POST /admin/test-mattermost` - Test Mattermost

Full API documentation available at `/docs` when running.

---

## 🔐 Security

### What's Implemented
✅ CSRF protection with token validation  
✅ Rate limiting (login, API, scans)  
✅ Secure HTTP headers (CSP, HSTS, X-Frame-Options)  
✅ Input validation and sanitization  
✅ SQL injection prevention (ORM)  
✅ XSS protection (Content-Security-Policy)  
✅ Audit logging of security events  
✅ Password strength validation  
✅ JWT authentication  
✅ Role-based access control  

### Before Production
- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Enable HTTPS/TLS with valid certificate
- [ ] Update CORS `allowed_origins`
- [ ] Configure secure database password
- [ ] Setup automated backups
- [ ] Enable HSTS header
- [ ] Review audit logs regularly

See [FEATURES_SECURITY.md](./FEATURES_SECURITY.md) for detailed security documentation.

---

## 🐳 Docker & Deployment

### Local Development
```bash
docker-compose up -d
```

### Production Deployment
See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for:
- Docker production setup
- Linux server installation
- Cloud platform deployment (AWS, Heroku, DigitalOcean)
- SSL/TLS configuration
- Database backups
- Monitoring setup

---

## 📊 Technology Stack

**Backend**:
- FastAPI 0.110.0+ - Modern async web framework
- SQLAlchemy 2.0+ - ORM database
- PostgreSQL 12+ - Production database
- APScheduler - Scheduled tasks
- aiohttp - Async HTTP client

**Security**:
- Python-jose - JWT tokens
- Passlib/Bcrypt - Password hashing
- Slowapi - Rate limiting
- Pydantic - Data validation

**Frontend**:
- HTML5/CSS3 - Modern web standards
- Vanilla JavaScript - No framework dependencies
- Glassmorphism design - Modern aesthetic

**DevOps**:
- Docker & Docker Compose
- Nginx - Reverse proxy
- Gunicorn/Uvicorn - App servers

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📞 Support

- Check [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for common issues
- Review API docs at `/docs` endpoint
- Check application logs in `logs/` directory

---

## 📈 Roadmap

Future enhancements:
- [ ] Shodan API integration for advanced scanning
- [ ] VirusTotal malware detection
- [ ] Email alerts
- [ ] Export reports (PDF, CSV, JSON)
- [ ] Vulnerability trend analysis
- [ ] Multi-domain group management
- [ ] WebSocket real-time updates
- [ ] GraphQL API

---

## ✅ Version History

### v2.0.0 (December 14, 2024) ✨ Latest
- ✅ Added vulnerability scanning API
- ✅ Fixed Mattermost notifications
- ✅ Enhanced security features (CSRF, rate limiting, secure headers)
- ✅ Improved frontend UI/UX
- ✅ Comprehensive documentation
- ✅ Production deployment guide

### v1.0.0 (Earlier)
- SSL certificate monitoring
- Domain expiration tracking
- User authentication
- Notification support

---

**🚀 Ready to Use!** Start monitoring your SSL certificates and domain security today.

For detailed setup, see [INSTALLATION.md](./INSTALLATION.md)

```
.
├── app/                          # Main application package
│   ├── core/                     # Core functionality
│   │   ├── config.py            # Configuration management (Pydantic)
│   │   └── security.py          # Authentication & JWT utilities
│   ├── db/                       # Database layer
│   │   └── session.py           # SQLAlchemy session & engine setup
│   ├── models/                   # SQLAlchemy ORM models
│   │   └── all_models.py        # User, Domain, AppSettings models
│   ├── routers/                  # API route handlers
│   │   ├── auth.py              # Authentication endpoints
│   │   ├── users.py             # User management endpoints
│   │   ├── domains.py           # Domain management endpoints
│   │   └── dashboard.py         # Dashboard & admin endpoints
│   ├── services/                 # Business logic
│   │   ├── checker.py           # SSL & domain checking logic
│   │   ├── jobs.py              # Scheduled jobs
│   │   └── notifier.py          # Notification services (Telegram, Mattermost, etc.)
│   └── schemas/                  # Pydantic request/response models
│       └── schemas.py           # Data validation schemas
├── scripts/                      # Utility scripts
│   ├── reset_db.py              # Database reset utility
│   └── debug_ir.py              # Domain debugging tool
├── static/                       # Frontend files
│   ├── login.html
│   ├── dashboard.html
│   └── admin.html
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── docker-compose.yml          # Docker Compose configuration
├── Dockerfile                  # Docker image definition
└── .env                        # Environment variables (not in repo)
```

## Features

- **SSL Certificate Monitoring**: Automatic SSL expiration date checking
- **Domain Expiration Tracking**: Monitor domain registration expiry dates
- **Multi-User Support**: Admin and regular user roles
- **Notifications**: Send alerts via Telegram, Mattermost, or webhooks
- **Scheduled Checks**: Configurable automated checking intervals
- **Web Dashboard**: User-friendly dashboard for managing domains and viewing status

## Requirements

- Python 3.8+
- PostgreSQL 12+
- Docker & Docker Compose (optional)

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd ssl-check-refac
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
# Edit .env with your database and API credentials
```

### 5. Initialize database

```bash
python scripts/reset_db.py
```

### 6. Run the application

```bash
python main.py
```

Visit `http://localhost:8000` in your browser.

## Configuration

Environment variables in `.env`:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/sslchecker_db

# Security
SECRET_KEY=your-secret-key-here

# Admin Credentials
DEFAULT_ADMIN_USER=admin
DEFAULT_ADMIN_PASSWORD=secure-password

# Check Interval
CHECK_INTERVAL_HOURS=24

# SSL Expiry Warning Threshold
EXPIRY_THRESHOLD_DAYS=10

# Logging
LOG_LEVEL=INFO
```

## Docker Deployment

```bash
docker-compose up -d
```

This will:
- Start a PostgreSQL database
- Build and run the FastAPI application
- Create the necessary tables and default admin user

## API Documentation

Interactive API documentation is available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Development

### Reset Database

To reset the database during development:

```bash
python scripts/reset_db.py
```

### Debug Domain Checking

To debug domain checking issues:

```bash
python scripts/debug_ir.py
```

## Code Quality

The project follows these conventions:

- Type hints on functions and methods
- Comprehensive docstrings
- Organized imports with comments
- Single responsibility principle
- Proper error handling

## License

[Add your license here]

## Support

For issues or questions, please open an issue in the repository.
