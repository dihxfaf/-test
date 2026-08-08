import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, BigInteger
from sqlalchemy.orm import relationship
from app.database import Base

class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Inbound(Base):
    __tablename__ = "inbounds"
    id = Column(Integer, primary_key=True, index=True)
    tag = Column(String, unique=True, default=lambda: f"inbound-{uuid.uuid4().hex[:8]}")
    protocol = Column(String, default="vless")
    listen = Column(String, default="0.0.0.0")
    port = Column(Integer)
    external_port = Column(Integer, default=443)
    domain = Column(String)
    path = Column(String, default="/graphql")
    network = Column(String, default="ws")
    security = Column(String, default="none")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    users = relationship("User", back_populates="inbound", cascade="all, delete-orphan")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    inbound_id = Column(Integer, ForeignKey("inbounds.id"))
    uuid = Column(String, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, default="user")
    traffic_limit = Column(BigInteger, default=0)      # bytes, 0 = unlimited
    traffic_used = Column(BigInteger, default=0)
    expire_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    sub_token = Column(String, unique=True, index=True, default=lambda: uuid.uuid4().hex)
    inbound = relationship("Inbound", back_populates="users")
