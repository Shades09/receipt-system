from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Receipt(Base):
    __tablename__ = "receipts"
    id = Column(Integer, primary_key=True, index=True)
    customer = Column(String, nullable=False)
    tax = Column(Float, default=0, nullable=False)
    discount = Column(Float, default=0, nullable=False)
    payment = Column(String, nullable=False)
    total = Column(Float, default=0, nullable=False)
    items = relationship(
        "Item",
        back_populates="receipt",
        cascade="all, delete-orphan"
    )

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    qty = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    receipt_id = Column(Integer, ForeignKey("receipts.id"), nullable=False)
    receipt = relationship("Receipt", back_populates="items")
