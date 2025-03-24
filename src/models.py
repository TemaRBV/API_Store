from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    info = Column(String, nullable=False)
    cost = Column(Integer, nullable=False)
    amount = Column(Integer, nullable=False)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.now().date(), nullable=False)
    status = Column(String, nullable=False)


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    order_amount = Column(Integer, nullable=False)

    #Уникальный составной индекс для order_id и product_id
    __table_args__ = (
           UniqueConstraint('order_id', 'product_id', name='uq_order_product'),
    )
