from concurrent.futures import ThreadPoolExecutor

from sqlalchemy.orm import sessionmaker

from app import models
from app.db import engine
from app.services import create_item, log_sale

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def seed_item(db_session, qty=10):
    item = create_item(
        db_session,
        {
            "sku": "SODA-123",
            "name": "Test Cola",
            "category": "Sodas",
            "quantity_on_hand": qty,
            "par_level": 4,
            "reorder_quantity": 12,
            "unit": "each",
            "sell_by_tracked": False,
            "cost": 1.0,
            "price": 2.0,
            "supplier_id": None,
        },
    )
    return item


def test_oversell_prevention(client, db_session):
    item = seed_item(db_session, qty=5)
    response = client.post("/sales", json={"item_id": item.id, "quantity": 6})
    assert response.status_code == 400
    assert "oversell" in response.json()["detail"].lower()


def test_concurrent_stock_updates_correctness(db_session):
    item = seed_item(db_session, qty=10)

    def run_sale():
        local = SessionLocal()
        try:
            log_sale(local, item.id, 1)
            return True
        except Exception:
            return False
        finally:
            local.close()

    with ThreadPoolExecutor(max_workers=12) as pool:
        results = list(pool.map(lambda _: run_sale(), range(12)))

    db_session.expire_all()
    refreshed = db_session.get(models.Item, item.id)
    assert sum(results) == 10
    assert refreshed.quantity_on_hand == 0
