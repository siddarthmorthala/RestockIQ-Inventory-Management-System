from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(120))
    phone: Mapped[str] = mapped_column(String(40))
    average_lead_time_days: Mapped[int] = mapped_column(Integer, default=7)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    items = relationship("Item", back_populates="supplier")


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sku: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    category: Mapped[str] = mapped_column(String(80), index=True)
    unit: Mapped[str] = mapped_column(String(30), default="each")
    quantity_on_hand: Mapped[int] = mapped_column(Integer, default=0)
    par_level: Mapped[int] = mapped_column(Integer, default=12)
    reorder_quantity: Mapped[int] = mapped_column(Integer, default=24)
    sell_by_tracked: Mapped[bool] = mapped_column(Boolean, default=False)
    cost: Mapped[float] = mapped_column(Float, default=0.0)
    price: Mapped[float] = mapped_column(Float, default=0.0)
    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("suppliers.id"), nullable=True)

    supplier = relationship("Supplier", back_populates="items")
    lots = relationship("InventoryLot", back_populates="item", cascade="all, delete-orphan")
    sales = relationship("Sale", back_populates="item", cascade="all, delete-orphan")
    shipments = relationship("Shipment", back_populates="item", cascade="all, delete-orphan")


class InventoryLot(Base):
    __tablename__ = "inventory_lots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), index=True)
    quantity_remaining: Mapped[int] = mapped_column(Integer)
    received_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    sell_by_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    item = relationship("Item", back_populates="lots")


class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), index=True)
    quantity: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    item = relationship("Item", back_populates="sales")


class Shipment(Base):
    __tablename__ = "shipments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), index=True)
    quantity: Mapped[int] = mapped_column(Integer)
    received_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    sell_by_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    item = relationship("Item", back_populates="shipments")
