import uuid as uuid_lib
from datetime import datetime
from sqlalchemy.orm import Session
from app import models, schemas
from app.auth import get_password_hash

# ---------- Admin ----------
def get_admin_by_username(db: Session, username: str):
    return db.query(models.Admin).filter(models.Admin.username == username).first()

def create_admin(db: Session, username: str, password: str):
    admin = models.Admin(username=username, hashed_password=get_password_hash(password))
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin

# ---------- Inbounds ----------
def get_inbounds(db: Session):
    inbounds = db.query(models.Inbound).all()
    for ib in inbounds:
        ib.user_count = len(ib.users)
    return inbounds

def get_inbound(db: Session, inbound_id: int):
    return db.query(models.Inbound).filter(models.Inbound.id == inbound_id).first()

def create_inbound(db: Session, inbound: schemas.InboundCreate):
    db_inbound = models.Inbound(**inbound.dict())
    db.add(db_inbound)
    db.commit()
    db.refresh(db_inbound)
    return db_inbound

def delete_inbound(db: Session, inbound_id: int):
    db_inbound = get_inbound(db, inbound_id)
    if db_inbound:
        db.delete(db_inbound)
        db.commit()
    return db_inbound

# ---------- Users ----------
def get_users_by_inbound(db: Session, inbound_id: int):
    return db.query(models.User).filter(models.User.inbound_id == inbound_id).all()

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_sub_token(db: Session, token: str):
    return db.query(models.User).filter(models.User.sub_token == token).first()

def create_user(db: Session, inbound_id: int, user_data: schemas.UserCreate):
    traffic_bytes = int(user_data.traffic_limit_gb * 1024**3)
    db_user = models.User(
        inbound_id=inbound_id,
        uuid=str(uuid_lib.uuid4()),
        email=user_data.email or f"user_{uuid_lib.uuid4().hex[:6]}",
        traffic_limit=traffic_bytes,
        expire_at=user_data.expire_at,
        sub_token=uuid_lib.uuid4().hex
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = get_user_by_id(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user

def update_user_traffic(db: Session, email: str, new_used: int):
    user = db.query(models.User).filter(models.User.email == email).first()
    if user:
        user.traffic_used = new_used
        db.commit()

def deactivate_expired_users(db: Session):
    now = datetime.utcnow()
    expired_users = db.query(models.User).filter(
        models.User.expire_at.isnot(None),
        models.User.expire_at <= now,
        models.User.is_active == True
    ).all()
    for user in expired_users:
        user.is_active = False
    db.commit()
