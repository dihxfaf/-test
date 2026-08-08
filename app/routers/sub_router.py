import base64
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response, PlainTextResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, utils
import yaml

router = APIRouter(prefix="/sub", tags=["subscription"])

@router.get("/{token}")
def subscription(token: str, format: str = Query("base64", regex="^(base64|clash)$"), db: Session = Depends(get_db)):
    user = crud.get_user_by_sub_token(db, token)
    if not user:
        raise HTTPException(status_code=404, detail="Subscription not found")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is disabled")
    if user.expire_at and user.expire_at < __import__("datetime").datetime.utcnow():
        raise HTTPException(status_code=403, detail="Account expired")
    inbound = user.inbound
    if not inbound or not inbound.is_active:
        raise HTTPException(status_code=403, detail="Inbound not active")

    if format == "base64":
        link = utils.generate_config_link(inbound, user)
        if not link:
            raise HTTPException(status_code=500, detail="Could not generate config")
        # encode as base64 subscription format (multiple lines possible, here single)
        content = base64.b64encode(link.encode()).decode()
        return Response(content=content, media_type="text/plain")

    elif format == "clash":
        clash_config = utils.generate_clash_config(user, inbound)
        yaml_content = yaml.dump(clash_config, allow_unicode=True, default_flow_style=False)
        return Response(content=yaml_content, media_type="text/plain")
