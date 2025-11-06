from decimal import Decimal
from .db import SessionLocal
from .crud import create_order
import csv
from pathlib import Path


def seed_example():
    db = SessionLocal()
    demo_order = {
        "customer_id": 1,
        "items": [
            {
                "product_id": 100,
                "sku": "DEMO-100",
                "name": "Demo Product",
                "quantity": 2,
                "unit_price": Decimal("9.99"),
            }
        ],
        "order_total": Decimal("21.98"),  # precomputed: 2*9.99 + tax/shipping for demo
        "tax": Decimal("1.00"),
        "shipping": Decimal("0.00"),
    }
    order_id = create_order(db, demo_order)
    print(f"[seeds] created demo order id={order_id}")


def seed_from_csv(orders_csv: str, items_csv: str):
    """
    Load orders and items from two CSV files and insert them.
    Expected minimal columns:
      - orders_csv: order_id, customer_id, shipping, tax, order_total
      - items_csv: order_id, product_id, sku, name, quantity, unit_price

    This function will create a new order in the service DB for each unique order_id
    discovered in orders_csv. It is intended for development only.
    """
    orders_path = Path(orders_csv)
    items_path = Path(items_csv)
    if not orders_path.exists() or not items_path.exists():
        raise FileNotFoundError("CSV files not found")

    # load items grouped by order_id
    items_by_order = {}
    with items_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            oid = int(r["order_id"])
            items_by_order.setdefault(oid, []).append(
                {
                    "product_id": int(r["product_id"]),
                    "sku": r["sku"],
                    "name": r.get("name", ""),
                    "quantity": int(r["quantity"]),
                    "unit_price": Decimal(r["unit_price"]),
                }
            )

    # for each order row, create a corresponding order in DB using grouped items
    with orders_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        db = SessionLocal()
        created = 0
        for r in reader:
            oid = int(r["order_id"])
            customer_id = int(r.get("customer_id", 0) or 0)
            shipping = Decimal(r.get("shipping", "0") or "0")
            tax = Decimal(r.get("tax", "0") or "0")
            order_total = Decimal(r.get("order_total", "0") or "0")
            items = items_by_order.get(oid, [])
            if not items:
                print(f"[seeds] skipping order {oid}: no items found")
                continue
            # create order
            create_order(
                db,
                {
                    "customer_id": customer_id,
                    "items": items,
                    "order_total": order_total,
                    "tax": tax,
                    "shipping": shipping,
                },
            )
            created += 1
        print(f"[seeds] seeded {created} orders from CSVs")