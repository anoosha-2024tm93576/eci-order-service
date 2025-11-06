from sqlalchemy import select, insert
from .models import orders, order_items, idempotency
from .db import SessionLocal
from decimal import Decimal
from sqlalchemy.exc import IntegrityError

from app import db


def create_idempotency_key(db, key: str):
    try:
        db.execute(insert(idempotency).values(key=key))
        db.commit()
        return True
    except IntegrityError:
        db.rollback()
    return False


def create_order(db, order, subtotal, tax, total, items):
    with db.begin():
        # Insert into orders table
        result = db.execute(insert(orders).values(
            customer_id=order.customer_id,
            status='CREATED',
            payment_status='PENDING',
            shipping=order.shipping,
            tax=tax,
            order_total=total
        ))
        order_id = result.inserted_primary_key[0]

        # Insert items
        for it in items:
            db.execute(insert(order_items).values(
                order_id=order_id,
                product_id=it['product_id'],
                sku=it['sku'],
                name=it['name'],
                quantity=it['quantity'],
                unit_price=it['unit_price']
            ))

        # Return a dict (so caller can access easily)
        return {"id": order_id}



def get_order(db, order_id: int):
    o = db.execute(select(orders).where(orders.c.id==order_id)).mappings().first()
    if not o:
        return None
    items = db.execute(select(order_items).where(order_items.c.order_id==order_id)).mappings().all()
    o = dict(o)
    o['items'] = [dict(i) for i in items]
    return o


def update_order_status(db, order_id: int, status: str, payment_status: str=None):
    with db.begin():
        upd = { 'status': status }
        if payment_status is not None:
            upd['payment_status'] = payment_status
        db.execute(orders.update().where(orders.c.id==order_id).values(**upd))