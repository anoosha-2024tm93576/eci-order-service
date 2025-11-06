from sqlalchemy import (
Table, Column, Integer, String, DateTime, Numeric, ForeignKey, Text, Enum, func, Boolean
)
from sqlalchemy.orm import registry, relationship
from .db import metadata


mapper_registry = registry()


orders = Table(
    'orders', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('customer_id', Integer, nullable=False),
    Column('status', String(30), nullable=False, default='CREATED'),
    Column('payment_status', String(30), nullable=False, default='PENDING'),
    Column('order_total', Numeric(12,2), nullable=False, default=0.00),
    Column('tax', Numeric(12,2), nullable=False, default=0.00),
    Column('shipping', Numeric(12,2), nullable=False, default=0.00),
    Column('signature', String(128), nullable=True),
    Column('created_at', DateTime, server_default=func.now())
)


order_items = Table(
    'order_items', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('order_id', Integer, ForeignKey('orders.id', ondelete='CASCADE'), nullable=False),
    Column('product_id', Integer, nullable=False),
    Column('sku', String(64), nullable=False),
    Column('name', String(255), nullable=False),
    Column('quantity', Integer, nullable=False),
    Column('unit_price', Numeric(12,2), nullable=False)
)


idempotency = Table(
    'idempotency_keys', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('key', String(128), unique=True, nullable=False),
    Column('created_at', DateTime, server_default=func.now())
)