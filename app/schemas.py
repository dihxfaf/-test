from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

# Auth
class Token(BaseModel):
    access_token: str
    token_type: str

class AdminOut(BaseModel):
    username: str

class ChangePassword(BaseModel):
    old_password: str
    new_password: str

# Inbound
class InboundBase(BaseModel):
    protocol: str = "vless"
    port: int
    external_port: int = 443
    domain: str
    path: str = "/graphql"
    network: str = "ws"
    security: str = "none"

class InboundCreate(InboundBase):
    pass

class InboundOut(InboundBase):
    id: int
    tag: str
    is_active: bool
    created_at: datetime
    user_count: Optional[int] = 0

    class Config:
        from_attributes = True

# User
class UserBase(BaseModel):
    traffic_limit_gb: float = 0.0
    expire_at: Optional[datetime] = None
    email: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserOut(UserBase):
    id: int
    inbound_id: int
    uuid: str
    traffic_used: int
    is_active: bool
    created_at: datetime
    sub_token: str
    config_link: Optional[str] = None
    qr_code_data: Optional[str] = None

    class Config:
        from_attributes = True
