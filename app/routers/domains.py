import csv
import io
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.db.session import get_db
from app.models.all_models import Domain, User, DomainHistory
from app.schemas.schemas import DomainCreate, DomainUpdate
from app.core.security import get_current_admin, get_current_user
from app.core.config import settings

router = APIRouter()

def clean_url(url: str) -> str:
    if not url: return ""
    # Remove protocol
    url = url.replace("https://", "").replace("http://", "")
    # Remove path
    url = url.split("/")[0]
    # Remove www. (optional)
    url = url.replace("www.", "")
    return url.strip()

@router.get("/list-only")
def get_domains_list(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    domains = db.query(Domain).all()
    return {"domains": domains, "is_admin": user.role == "admin"}

@router.get("/")
def get_domains(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    return db.query(Domain).all()

@router.post("/")
def add_domain(domain_in: DomainCreate, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    # Clean URL before saving
    cleaned_url = clean_url(domain_in.url)
    
    if not cleaned_url:
        raise HTTPException(status_code=400, detail="Invalid domain URL")

    if db.query(Domain).filter(Domain.url == cleaned_url).first():
        raise HTTPException(status_code=400, detail="Domain already exists")
    
    new_domain = Domain(
        url=cleaned_url,
        custom_ssl_danger=domain_in.ssl_danger,
        custom_ssl_warning=domain_in.ssl_warning,
        custom_domain_danger=domain_in.domain_danger,
        custom_domain_warning=domain_in.domain_warning,
        notify_on_warning=domain_in.notify_warning,
        notify_on_critical=domain_in.notify_critical,
        monitor_ssl=domain_in.monitor_ssl,
        monitor_domain=domain_in.monitor_domain
    )
    db.add(new_domain)
    db.commit()
    return {"status": "created", "url": cleaned_url}

@router.put("/{did}")
def update_domain(did: int, domain_in: DomainUpdate, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    domain = db.query(Domain).filter(Domain.id == did).first()
    if not domain: raise HTTPException(404, "Domain not found")
    
    domain.custom_ssl_danger = domain_in.ssl_danger
    domain.custom_ssl_warning = domain_in.ssl_warning
    domain.custom_domain_danger = domain_in.domain_danger
    domain.custom_domain_warning = domain_in.domain_warning
    domain.notify_on_warning = domain_in.notify_warning
    domain.notify_on_critical = domain_in.notify_critical
    domain.monitor_ssl = domain_in.monitor_ssl
    domain.monitor_domain = domain_in.monitor_domain
    
    db.commit()
    return {"status": "updated"}

@router.delete("/{did}")
def delete_domain(did: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    domain = db.query(Domain).filter(Domain.id == did).first()
    if not domain: raise HTTPException(404, "Domain not found")
    db.delete(domain)
    db.commit()
    return {"status": "deleted"}

@router.get("/export")
def export_domains(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None: raise HTTPException(status_code=401)
    except JWTError: raise HTTPException(status_code=401)

    user = db.query(User).filter(User.username == username).first()
    if not user or user.role != "admin": raise HTTPException(status_code=403)

    domains = db.query(Domain).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'URL', 'SSL_Days', 'Domain_Days', 'Status', 'Monitor_SSL', 'Monitor_Dom'])
    
    for d in domains:
        last_hist = db.query(DomainHistory).filter(DomainHistory.domain_id == d.id).order_by(DomainHistory.checked_at.desc()).first()
        writer.writerow([
            d.id, d.url, 
            last_hist.ssl_days if last_hist else 'N/A',
            last_hist.domain_days if last_hist else 'N/A',
            last_hist.overall_status if last_hist else 'No Data',
            d.monitor_ssl, d.monitor_domain
        ])
    
    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=domains_report.csv"})

@router.post("/import")
async def import_domains(file: UploadFile = File(...), db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    content = await file.read()
    text_content = content.decode("utf-8")
    added_count = 0
    skipped_count = 0
    lines = text_content.splitlines()
    for line in lines:
        if not line.strip() or 'URL' in line: continue
        parts = line.split(',')
        raw_url = parts[1] if len(parts) > 1 else parts[0]
        
        # Clean URL in import too
        url = clean_url(raw_url)
        
        if not url: continue

        if db.query(Domain).filter(Domain.url == url).first():
            skipped_count += 1
            continue
        db.add(Domain(url=url))
        added_count += 1
    db.commit()
    return {"status": "finished", "added": added_count, "skipped": skipped_count}