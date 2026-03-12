from datetime import date, timedelta

from .db import Base, SessionLocal, engine
from . import models
from .services import receive_shipment


def run_seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if db.query(models.Item).count() > 0:
        db.close()
        return

    suppliers = [
        models.Supplier(
            name="Lone Star Spirits Wholesale",
            email="orders@lonestarspirits.example",
            phone="972-555-0141",
            average_lead_time_days=4,
            notes="Primary Plano-area spirits wholesaler; fast tequila and bourbon turns.",
        ),
        models.Supplier(
            name="Metroplex Beverage Partners",
            email="restock@metroplexbev.example",
            phone="214-555-0186",
            average_lead_time_days=3,
            notes="Beer, RTD cocktails, and soda mixers for weekly replenishment.",
        ),
        models.Supplier(
            name="Red River Craft Distribution",
            email="sales@redrivercraft.example",
            phone="469-555-0112",
            average_lead_time_days=6,
            notes="Craft beer and seasonal releases with shorter shelf life.",
        ),
        models.Supplier(
            name="Oak Cliff Imports",
            email="orders@oakcliffimports.example",
            phone="972-555-0129",
            average_lead_time_days=7,
            notes="Imported wines, aperitifs, and specialty liqueurs.",
        ),
    ]
    db.add_all(suppliers)
    db.commit()
    for supplier in suppliers:
        db.refresh(supplier)

    supplier_map = {s.name: s.id for s in suppliers}

    items = [
        models.Item(sku="ANG-VOD-001", name="Hillcrest Vodka 750ml", category="Spirits", par_level=14, reorder_quantity=24, quantity_on_hand=0, supplier_id=supplier_map["Lone Star Spirits Wholesale"], price=18.99, cost=10.10),
        models.Item(sku="ANG-BRB-014", name="Cedar Barrel Bourbon 750ml", category="Spirits", par_level=10, reorder_quantity=18, quantity_on_hand=0, supplier_id=supplier_map["Lone Star Spirits Wholesale"], price=34.99, cost=19.25),
        models.Item(sku="ANG-TQL-022", name="Blue Mesa Tequila Blanco 750ml", category="Spirits", par_level=12, reorder_quantity=24, quantity_on_hand=0, supplier_id=supplier_map["Lone Star Spirits Wholesale"], price=29.99, cost=16.40),
        models.Item(sku="ANG-BER-031", name="Pecan Trail Lager 6-Pack", category="Beer", par_level=20, reorder_quantity=36, quantity_on_hand=0, supplier_id=supplier_map["Metroplex Beverage Partners"], price=10.99, cost=5.35),
        models.Item(sku="ANG-IPA-044", name="Red Dirt IPA 6-Pack", category="Craft Beer", par_level=18, reorder_quantity=30, quantity_on_hand=0, supplier_id=supplier_map["Red River Craft Distribution"], price=11.99, cost=5.95, sell_by_tracked=True),
        models.Item(sku="ANG-SLT-052", name="Lemon Ranch Water 4-Pack", category="RTD Cocktails", par_level=16, reorder_quantity=28, quantity_on_hand=0, supplier_id=supplier_map["Metroplex Beverage Partners"], price=12.49, cost=6.10),
        models.Item(sku="ANG-MXR-060", name="Top Shelf Tonic 4-Pack", category="Mixers", par_level=15, reorder_quantity=24, quantity_on_hand=0, supplier_id=supplier_map["Metroplex Beverage Partners"], price=5.99, cost=2.40),
        models.Item(sku="ANG-JCE-073", name="Fresh Press Margarita Mix", category="Mixers", par_level=12, reorder_quantity=20, quantity_on_hand=0, supplier_id=supplier_map["Metroplex Beverage Partners"], price=6.49, cost=2.95, sell_by_tracked=True),
        models.Item(sku="ANG-WIN-081", name="North Ridge Cabernet 750ml", category="Wine", par_level=9, reorder_quantity=15, quantity_on_hand=0, supplier_id=supplier_map["Oak Cliff Imports"], price=16.99, cost=8.50),
        models.Item(sku="ANG-GIN-092", name="Juniper House Gin 750ml", category="Spirits", par_level=8, reorder_quantity=12, quantity_on_hand=0, supplier_id=supplier_map["Oak Cliff Imports"], price=27.99, cost=14.20),
    ]
    db.add_all(items)
    db.commit()
    for item in db.query(models.Item).all():
        sell_by = date.today() + timedelta(days=12) if item.sell_by_tracked else None
        receive_shipment(db, item.id, item.reorder_quantity, sell_by)
    db.close()


if __name__ == "__main__":
    run_seed()
