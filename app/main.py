from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.database import engine, Base, SessionLocal
from app import auth, crud
from app.routers import auth_router, inbound_router, user_router, sub_router
from app.xray_api import start_traffic_monitor
from app.background import expire_checker
import os
import asyncio

app = FastAPI(title="Xray Panel")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(auth_router.router)
app.include_router(inbound_router.router)
app.include_router(user_router.router)
app.include_router(sub_router.router)

@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    admin_user = os.getenv("ADMIN_USERNAME", "admin")
    if not crud.get_admin_by_username(db, admin_user):
        crud.create_admin(db, admin_user, os.getenv("ADMIN_PASSWORD", "password"))
    db.close()
    start_traffic_monitor()
    asyncio.create_task(expire_checker())

# Frontend routes
@app.get("/", response_class=HTMLResponse)
def root(request: Request, admin=Depends(auth.get_current_admin)):
    return RedirectResponse(url="/dashboard")

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, admin=Depends(auth.get_current_admin)):
    db = SessionLocal()
    inbounds = crud.get_inbounds(db)
    db.close()
    return templates.TemplateResponse("dashboard.html", {"request": request, "inbounds": inbounds, "admin": admin})

@app.get("/inbounds/{inbound_id}", response_class=HTMLResponse)
def inbound_page(request: Request, inbound_id: int, admin=Depends(auth.get_current_admin)):
    db = SessionLocal()
    inbound = crud.get_inbound(db, inbound_id)
    if not inbound:
        return RedirectResponse("/dashboard")
    users = crud.get_users_by_inbound(db, inbound_id)
    for u in users:
        u.config_link = utils.generate_config_link(inbound, u) if hasattr(utils, 'generate_config_link') else None
        u.qr_code_data = utils.generate_qr_code_base64(u.config_link) if u.config_link else None
    db.close()
    return templates.TemplateResponse("inbound.html", {
        "request": request,
        "inbound": inbound,
        "users": users
    })
