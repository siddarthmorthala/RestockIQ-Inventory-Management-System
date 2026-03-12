from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta
from threading import Lock

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import models

_inventory_lock = Lock()


def create_supplier(db: Session, payload: dict) -> models.Supplier:
    supplier = models.Supplier(**payload)
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


def create_item(db: Session, payload: dict) -> models.Item:
    item = models.Item(**payload)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def list_suppliers(db: Session) -> list[models.Supplier]:
    return list(db.scalars(select(models.Supplier).order_by(models.Supplier.name)))


def list_items(db: Session) -> list[models.Item]:
    return list(db.scalars(select(models.Item).order_by(models.Item.name)))


def receive_shipment(db: Session, item_id: int, quantity: int, sell_by_date: date | None = None) -> models.Item:
    item = db.get(models.Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    with _inventory_lock:
        item.quantity_on_hand += quantity
        shipment = models.Shipment(item_id=item_id, quantity=quantity, sell_by_date=sell_by_date)
        db.add(shipment)
        lot = models.InventoryLot(item_id=item_id, quantity_remaining=quantity, sell_by_date=sell_by_date)
        db.add(lot)
        db.commit()
        db.refresh(item)
    return item


def log_sale(db: Session, item_id: int, quantity: int) -> models.Item:
    item = db.get(models.Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    with _inventory_lock:
        db.refresh(item)
        if item.quantity_on_hand < quantity:
            raise HTTPException(status_code=400, detail="Insufficient stock; oversell prevented")

        item.quantity_on_hand -= quantity
        remaining = quantity
        lots = list(db.scalars(
            select(models.InventoryLot)
            .where(models.InventoryLot.item_id == item_id, models.InventoryLot.quantity_remaining > 0)
            .order_by(models.InventoryLot.sell_by_date.is_(None), models.InventoryLot.sell_by_date, models.InventoryLot.received_at)
        ))
        for lot in lots:
            if remaining == 0:
                break
            consume = min(lot.quantity_remaining, remaining)
            lot.quantity_remaining -= consume
            remaining -= consume

        db.add(models.Sale(item_id=item_id, quantity=quantity))
        db.commit()
        db.refresh(item)
    return item


def low_stock_alerts(db: Session) -> list[dict]:
    rows = db.execute(select(models.Item).where(models.Item.quantity_on_hand < models.Item.par_level).order_by(models.Item.quantity_on_hand)).scalars().all()
    return [
        {
            "item_id": row.id,
            "sku": row.sku,
            "name": row.name,
            "category": row.category,
            "quantity_on_hand": row.quantity_on_hand,
            "par_level": row.par_level,
        }
        for row in rows
    ]


def expiration_alerts(db: Session, days: int = 14) -> list[dict]:
    cutoff = date.today() + timedelta(days=days)
    lots = db.execute(
        select(models.InventoryLot, models.Item)
        .join(models.Item, models.Item.id == models.InventoryLot.item_id)
        .where(models.InventoryLot.sell_by_date.is_not(None), models.InventoryLot.sell_by_date <= cutoff, models.InventoryLot.quantity_remaining > 0)
        .order_by(models.InventoryLot.sell_by_date)
    ).all()
    payload = []
    for lot, item in lots:
        payload.append(
            {
                "item_id": item.id,
                "sku": item.sku,
                "name": item.name,
                "lot_id": lot.id,
                "quantity_remaining": lot.quantity_remaining,
                "sell_by_date": lot.sell_by_date,
                "days_until_sell_by": (lot.sell_by_date - date.today()).days,
            }
        )
    return payload


def reorder_suggestions(db: Session, window_days: int = 7) -> list[dict]:
    since = datetime.utcnow() - timedelta(days=window_days)
    sales_rows = db.execute(
        select(models.Sale.item_id, func.sum(models.Sale.quantity))
        .where(models.Sale.created_at >= since)
        .group_by(models.Sale.item_id)
    ).all()
    sales_by_item = defaultdict(int, sales_rows)

    items = db.execute(select(models.Item, models.Supplier).join(models.Supplier, isouter=True)).all()
    results = []
    for item, supplier in items:
        avg_sales = round(sales_by_item.get(item.id, 0) / window_days, 2)
        projected_need = max(item.par_level, int(avg_sales * max((supplier.average_lead_time_days if supplier else 7), 1)))
        if item.quantity_on_hand < item.par_level:
            suggested = max(item.reorder_quantity, projected_need - item.quantity_on_hand)
            results.append(
                {
                    "item_id": item.id,
                    "sku": item.sku,
                    "name": item.name,
                    "quantity_on_hand": item.quantity_on_hand,
                    "par_level": item.par_level,
                    "seven_day_avg_sales": avg_sales,
                    "suggested_reorder_qty": suggested,
                    "supplier_name": supplier.name if supplier else None,
                    "supplier_lead_time_days": supplier.average_lead_time_days if supplier else None,
                }
            )
    return sorted(results, key=lambda x: (x["quantity_on_hand"], -x["suggested_reorder_qty"]))
