import asyncio
from app.database import SessionLocal
from app import crud

async def expire_checker():
    while True:
        db = SessionLocal()
        crud.deactivate_expired_users(db)
        db.close()
        await asyncio.sleep(60)
