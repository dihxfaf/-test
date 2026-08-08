from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, auth, schemas

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    admin = crud.get_admin_by_username(db, form_data.username)
    if not admin or not auth.verify_password(form_data.password, admin.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = auth.create_access_token(data={"sub": admin.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.AdminOut)
def read_admin(current_admin=Depends(auth.get_current_admin)):
    return current_admin

@router.post("/change-password")
def change_password(data: schemas.ChangePassword, db: Session = Depends(get_db), current_admin=Depends(auth.get_current_admin)):
    if not auth.verify_password(data.old_password, current_admin.hashed_password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    current_admin.hashed_password = auth.get_password_hash(data.new_password)
    db.commit()
    return {"message": "Password updated"}
