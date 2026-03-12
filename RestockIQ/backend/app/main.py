from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import schemas, services
from .db import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(title="RestockIQ API", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok", "app": "RestockIQ"}


@app.get("/items", response_model=list[schemas.ItemRead])
def get_items(db: Session = Depends(get_db)):
    return services.list_items(db)


@app.post("/items", response_model=schemas.ItemRead)
def create_item(payload: schemas.ItemCreate, db: Session = Depends(get_db)):
    return services.create_item(db, payload.model_dump())


@app.get("/suppliers", response_model=list[schemas.SupplierRead])
def get_suppliers(db: Session = Depends(get_db)):
    return services.list_suppliers(db)


@app.post("/suppliers", response_model=schemas.SupplierRead)
def create_supplier(payload: schemas.SupplierCreate, db: Session = Depends(get_db)):
    return services.create_supplier(db, payload.model_dump())


@app.get("/alerts/low-stock", response_model=list[schemas.AlertRead])
def get_low_stock_alerts(db: Session = Depends(get_db)):
    return services.low_stock_alerts(db)


@app.get("/alerts/expiring", response_model=list[schemas.ExpirationAlertRead])
def get_expiration_alerts(days: int = 14, db: Session = Depends(get_db)):
    return services.expiration_alerts(db, days=days)


@app.get("/reorder-suggestions", response_model=list[schemas.ReorderSuggestionRead])
def get_reorder_suggestions(window_days: int = 7, db: Session = Depends(get_db)):
    return services.reorder_suggestions(db, window_days=window_days)


@app.post("/sales", response_model=schemas.ItemRead)
def create_sale(payload: schemas.SaleCreate, db: Session = Depends(get_db)):
    return services.log_sale(db, payload.item_id, payload.quantity)


@app.post("/shipments", response_model=schemas.ItemRead)
def create_shipment(payload: schemas.ShipmentCreate, db: Session = Depends(get_db)):
    return services.receive_shipment(db, payload.item_id, payload.quantity, payload.sell_by_date)
