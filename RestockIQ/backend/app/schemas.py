from datetime import date, datetime

from pydantic import BaseModel, Field


class SupplierBase(BaseModel):
    name: str
    email: str
    phone: str
    average_lead_time_days: int = 7
    notes: str | None = None


class SupplierCreate(SupplierBase):
    pass


class SupplierRead(SupplierBase):
    id: int

    class Config:
        from_attributes = True


class ItemBase(BaseModel):
    sku: str
    name: str
    category: str
    unit: str = "each"
    par_level: int = 12
    reorder_quantity: int = 24
    sell_by_tracked: bool = False
    cost: float = 0.0
    price: float = 0.0
    supplier_id: int | None = None


class ItemCreate(ItemBase):
    quantity_on_hand: int = 0


class ItemRead(ItemBase):
    id: int
    quantity_on_hand: int

    class Config:
        from_attributes = True


class SaleCreate(BaseModel):
    item_id: int
    quantity: int = Field(gt=0)


class ShipmentCreate(BaseModel):
    item_id: int
    quantity: int = Field(gt=0)
    sell_by_date: date | None = None


class InventoryLotRead(BaseModel):
    id: int
    item_id: int
    quantity_remaining: int
    received_at: datetime
    sell_by_date: date | None = None

    class Config:
        from_attributes = True


class AlertRead(BaseModel):
    item_id: int
    sku: str
    name: str
    category: str
    quantity_on_hand: int
    par_level: int


class ExpirationAlertRead(BaseModel):
    item_id: int
    sku: str
    name: str
    lot_id: int
    quantity_remaining: int
    sell_by_date: date
    days_until_sell_by: int


class ReorderSuggestionRead(BaseModel):
    item_id: int
    sku: str
    name: str
    quantity_on_hand: int
    par_level: int
    seven_day_avg_sales: float
    suggested_reorder_qty: int
    supplier_name: str | None = None
    supplier_lead_time_days: int | None = None
