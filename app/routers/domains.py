from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.all_models import Domain, User
from app.schemas.schemas import DomainCreate, DomainUpdate
from app.core.security import get_current_admin, get_current_user

router = APIRouter()

# --- تغییر مهم: ارسال وضعیت ادمین در درخواست سریع ---
@router.get("/list-only")
def get_domains_list(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """
    لیست دامنه‌ها + وضعیت ادمین را برمی‌گرداند (برای لود آنی)
    """
    domains = db.query(Domain).all()
    return {
        "domains": domains,
        "is_admin": user.role == "admin"  # این خط باعث نمایش سریع دکمه می‌شود
    }
# ------------------------------------------------------

@router.get("/")
def get_domains(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    return db.query(Domain).all()

@router.post("/")
def add_domain(domain_in: DomainCreate, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    if db.query(Domain).filter(Domain.url == domain_in.url).first():
        raise HTTPException(status_code=400, detail="Domain already exists")
    
    new_domain = Domain(
        url=domain_in.url,
        custom_ssl_danger=domain_in.ssl_danger,
        custom_ssl_warning=domain_in.ssl_warning,
        custom_domain_danger=domain_in.domain_danger,
        custom_domain_warning=domain_in.domain_warning
    )
    db.add(new_domain)
    db.commit()
    return {"status": "created", "url": new_domain.url}

@router.put("/{did}")
def update_domain(did: int, domain_in: DomainUpdate, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    domain = db.query(Domain).filter(Domain.id == did).first()
    if not domain: raise HTTPException(404, "Domain not found")
    
    domain.custom_ssl_danger = domain_in.ssl_danger
    domain.custom_ssl_warning = domain_in.ssl_warning
    domain.custom_domain_danger = domain_in.domain_danger
    domain.custom_domain_warning = domain_in.domain_warning
    
    db.commit()
    return {"status": "updated"}

@router.delete("/{did}")
def delete_domain(did: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    domain = db.query(Domain).filter(Domain.id == did).first()
    if not domain: raise HTTPException(404, "Domain not found")
    db.delete(domain)
    db.commit()
    return {"status": "deleted"}