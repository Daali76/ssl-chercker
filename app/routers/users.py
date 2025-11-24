from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.all_models import User
from app.schemas.schemas import UserResponse, UserCreate, RoleUpdate
from app.core.security import get_current_admin, get_password_hash

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    return db.query(User).all()

@router.post("/create")
def create_user(user_in: UserCreate, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    if db.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    
    new_user = User(
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role
    )
    db.add(new_user)
    db.commit()
    return {"status": "created"}

@router.put("/{uid}/toggle-status")
def toggle_user_status(uid: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    user = db.query(User).filter(User.id == uid).first()
    if not user: raise HTTPException(404, "User not found")
    if user.username == admin.username: raise HTTPException(400, "Cannot disable yourself")
    
    user.disabled = not user.disabled
    db.commit()
    return {"status": "ok", "disabled": user.disabled}

@router.delete("/{uid}")
def delete_user(uid: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    user = db.query(User).filter(User.id == uid).first()
    if not user: raise HTTPException(404, "User not found")
    if user.username == admin.username: raise HTTPException(400, "Cannot delete yourself")
    
    db.delete(user)
    db.commit()
    return {"status": "deleted"}

@router.put("/{uid}/role")
def change_user_role(uid: int, role_data: RoleUpdate, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    user = db.query(User).filter(User.id == uid).first()
    if not user: raise HTTPException(404, "User not found")
    if user.username == admin.username: raise HTTPException(400, "Cannot change your own role")
    
    user.role = role_data.role
    db.commit()
    return {"status": "ok"}