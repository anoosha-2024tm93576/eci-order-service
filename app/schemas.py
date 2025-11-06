from pydantic import BaseModel
from typing import List, Optional

class OrderItem(BaseModel):
    product_id: int
    sku: str
    name: str
    quantity: int
    unit_price: float

class OrderCreate(BaseModel):
    customer_id: int
    items: List[OrderItem]
    shipping: float  # keep it as 'shipping' to match API

class OrderStatusUpdate(BaseModel):
    status: str
    payment_status: Optional[str] = None
