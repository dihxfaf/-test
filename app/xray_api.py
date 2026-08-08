import asyncio, httpx
from app.database import SessionLocal
from app import crud

XRAY_API_ADDR = "http://127.0.0.1:10085"

async def fetch_traffic():
    while True:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(f"{XRAY_API_ADDR}/stats/query", json={"pattern": "user>>>"})
                if resp.status_code == 200:
                    data = resp.json()
                    stat = data.get("stat", [])
                    user_traffic = {}
                    for item in stat:
                        name = item.get("name", "")
                        if "user>>>" not in name:
                            continue
                        parts = name.split(">>>")
                        if len(parts) == 5 and parts[2] == "traffic":
                            email = parts[1]
                            bytes_val = int(item.get("value", 0))
                            user_traffic[email] = user_traffic.get(email, 0) + bytes_val
                    db = SessionLocal()
                    for email, total_bytes in user_traffic.items():
                        crud.update_user_traffic(db, email, total_bytes)
                    db.close()
        except Exception:
            pass
        await asyncio.sleep(30)

def start_traffic_monitor():
    asyncio.create_task(fetch_traffic())
