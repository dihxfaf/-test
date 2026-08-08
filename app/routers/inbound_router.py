from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas, auth
from app.xray_manager import reload_xray

router = APIRouter(prefix="/inbounds", tags=["inbounds"])

@router.get("/", response_model=list[schemas.InboundOut])
def list_inbounds(db: Session = Depends(get_db), admin=Depends(auth.get_current_admin)):
    return crud.get_inbounds(db)

@router.post("/", response_model=schemas.InboundOut)
def create_inbound(inbound: schemas.InboundCreate, db: Session = Depends(get_db), admin=Depends(auth.get_current_admin)):
    db_inbound = crud.create_inbound(db, inbound)
    reload_xray()
    return db_inbound

@router.get("/{inbound_id}", response_model=schemas.InboundOut)
def get_inbound(inbound_id: int, db: Session = Depends(get_db), admin=Depends(auth.get_current_admin)):
    db_inbound = crud.get_inbound(db, inbound_id)
    if not db_inbound:
        raise HTTPException(status_code=404, detail="Inbound not found")
    return db_inbound

@router.delete("/{inbound_id}")
def delete_inbound(inbound_id: int, db: Session = Depends(get_db), admin=Depends(auth.get_current_admin)):
    crud.delete_inbound(db, inbound_id)
    reload_xray()
    return {"ok": True}
