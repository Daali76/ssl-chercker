import os
import asyncio
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import settings
from app.db.session import engine, Base, SessionLocal
from app.models.all_models import User, AppSettings
from app.core.security import get_password_hash
from app.routers import auth, users, domains, dashboard
from app.services.jobs import check_job

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"), format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(domains.router, prefix="/domains", tags=["Domains"])
app.include_router(dashboard.router, tags=["Dashboard"])

scheduler = AsyncIOScheduler()

@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    app_settings = db.query(AppSettings).first()
    if not app_settings:
        app_settings = AppSettings(id=1, check_interval_hours=24) 
        db.add(app_settings)
        db.commit()
    
    if not db.query(User).filter(User.username == settings.DEFAULT_ADMIN_USER).first():
        user = User(
            username=settings.DEFAULT_ADMIN_USER,
            hashed_password=get_password_hash(settings.DEFAULT_ADMIN_PASSWORD),
            role="admin"
        )
        db.add(user)
        db.commit()
    
    interval = app_settings.check_interval_hours if app_settings.check_interval_hours else 24
    logging.info(f"Scheduler started with interval: {interval} hours")
    
    scheduler.add_job(check_job, 'interval', hours=interval)
    scheduler.start()
    
    db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
 
