"""
SSL & Domain Checker Application.

Main FastAPI application entry point.
"""
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import settings
from app.db.session import engine, Base, SessionLocal
from app.models.all_models import User, AppSettings
from app.core.security import get_password_hash
from app.routers import auth, users, domains, dashboard, vulnerabilities
from app.services.jobs import check_job

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize scheduler
scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle - startup and shutdown events.
    
    This replaces the deprecated @app.on_event() decorators.
    """
    # Startup: Initialize database and start scheduler
    logger.info("Starting application...")
    
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        logger.warning("⚠️  Database unavailable. Running in limited mode.")
        logger.info("Hint: For local development, ensure PostgreSQL is running or use Docker: docker-compose up -d")
    
    db = SessionLocal()
    try:
        # Initialize app settings
        app_settings = db.query(AppSettings).first()
        if not app_settings:
            app_settings = AppSettings(id=1, check_interval_hours=24)
            db.add(app_settings)
            db.commit()
            logger.info("Created default app settings")
        
        # Create default admin user if not exists
        if not db.query(User).filter(User.username == settings.DEFAULT_ADMIN_USER).first():
            user = User(
                username=settings.DEFAULT_ADMIN_USER,
                hashed_password=get_password_hash(settings.DEFAULT_ADMIN_PASSWORD),
                role="admin"
            )
            db.add(user)
            db.commit()
            logger.info(f"Created default admin user: {settings.DEFAULT_ADMIN_USER}")
        
        # Start scheduler with configured interval
        interval = app_settings.check_interval_hours or 24
        logger.info(f"Starting scheduler with {interval} hour interval")
        
        scheduler.add_job(check_job, 'interval', hours=interval)
        scheduler.start()
        logger.info("✅ Scheduler started successfully")
        
    except Exception as e:
        logger.error(f"Error during startup initialization: {e}")
        logger.warning("App will start but some features may be unavailable")
    finally:
        db.close()
    
    yield
    
    # Shutdown: Gracefully stop scheduler
    logger.info("Shutting down application...")
    if scheduler.running:
        scheduler.shutdown()
        logger.info("✅ Scheduler shut down successfully")


# Initialize FastAPI app with lifespan
app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan
)

# Configure middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(domains.router, prefix="/domains", tags=["Domains"])
app.include_router(dashboard.router, tags=["Dashboard"])
app.include_router(vulnerabilities.router, tags=["Vulnerabilities"])



