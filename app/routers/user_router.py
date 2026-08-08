from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas, auth, utils, models
from app.xray_manager import reload_xray
from typing import List

router = APIRouter(prefix="/inbounds/{inbound_id}/users", tags=["users"])

@router.get("/", response_model=List[schemas.UserOut])
def list_users(inbound_id: int, db: Session = Depends(get_db), admin=Depends(auth.get_current_admin)):
    inbound = crud.get_inbound(db, inbound_id)
    if not inbound:
        raise HTTPException(status_code=404, detail="Inbound not found")
    users = crud.get_users_by_inbound(db, inbound_id)
    for u in users:
        u.config_link = utils.generate_config_link(inbound, u)
        u.qr_code_data = utils.generate_qr_code_base64(u.config_link) if u.config_link else None
    return users

@router.post("/", response_model=schemas.UserOut)
def create_user(inbound_id: int, user_data: schemas.UserCreate, db: Session = Depends(get_db), admin=Depends(auth.get_current_admin)):
    inbound = crud.get_inbound(db, inbound_id)
    if not inbound:
        raise HTTPException(status_code=404, detail="Inbound not found")
    db_user = crud.create_user(db, inbound_id, user_data)
    reload_xray()
    db_user.config_link = utils.generate_config_link(inbound, db_user)
    db_user.qr_code_data = utils.generate_qr_code_base64(db_user.config_link) if db_user.config_link else None
    return db_user

@router.get("/{user_id}", response_model=schemas.UserOut)
def get_user(inbound_id: int, user_id: int, db: Session = Depends(get_db), admin=Depends(auth.get_current_admin)):
    inbound = crud.get_inbound(db, inbound_id)
    user = db.query(models.User).filter(models.User.id == user_id, models.User.inbound_id == inbound_id).first()
    if not inbound or not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.config_link = utils.generate_config_link(inbound, user)
    user.qr_code_data = utils.generate_qr_code_base64(user.config_link) if user.config_link else None
    return user

@router.delete("/{user_id}")
def delete_user(inbound_id: int, user_id: int, db: Session = Depends(get_db), admin=Depends(auth.get_current_admin)):
    crud.delete_user(db, user_id)
    reload_xray()
    return {"ok": True}
