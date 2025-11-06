from fastapi import APIRouter, Header, HTTPException, status
from decimal import Decimal
from . import schemas, crud, db, utils

router = APIRouter(prefix="/v1")

# -------------------------------
# POST /v1/orders
# -------------------------------
@router.post("/orders", response_model=dict)
async def create_order(order: schemas.OrderCreate, idempotency_key: str = Header(None)):
    """Create a new order with items and idempotency key."""

    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Idempotency-Key header required")

    session = db.SessionLocal()

    try:
        # Prevent duplicate requests
        created = crud.create_idempotency_key(session, idempotency_key)
        if not created:
            raise HTTPException(status_code=409, detail="Duplicate request")

        # Calculate totals
        subtotal = Decimal("0")
        items = []
        for item in order.items:
            line_total = Decimal(item.unit_price) * item.quantity
            subtotal += line_total
            items.append({
                "product_id": item.product_id,
                "sku": item.sku,
                "name": item.name,
                "quantity": item.quantity,
                "unit_price": Decimal(item.unit_price)
            })

        tax = utils.bankers_round(subtotal * Decimal("0.05"))
        shipping_fee = Decimal(order.shipping)
        total = subtotal + tax + shipping_fee


        result = crud.create_order(session, order, subtotal, tax, total, items)
        order_id = result["id"]


        return {
            "order_id": order_id,
            "status": "CONFIRMED",
            "subtotal": str(subtotal),
            "tax": str(tax),
            "total": str(total)
        }

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()


# -------------------------------
# GET /v1/orders/{order_id}
# -------------------------------
@router.get("/orders/{order_id}", response_model=dict)
async def get_order(order_id: int):
    """Retrieve a single order with its items."""
    session = db.SessionLocal()
    try:
        order = crud.get_order(session, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        # Convert Decimals → str for JSON compatibility
        order["order_total"] = str(order["order_total"])
        order["tax"] = str(order["tax"])
        order["shipping"] = str(order["shipping"])
        for item in order["items"]:
            item["unit_price"] = str(item["unit_price"])

        return order
    finally:
        session.close()


# -------------------------------
# PATCH /v1/orders/{order_id}/status
# -------------------------------
@router.patch("/orders/{order_id}/status", response_model=dict)
async def update_order_status(order_id: int, update: schemas.OrderStatusUpdate):
    """Update order or payment status."""
    session = db.SessionLocal()
    try:
        crud.update_order_status(session, order_id, update.status, update.payment_status)
        session.commit()
        return {"order_id": order_id, "status": update.status}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()
