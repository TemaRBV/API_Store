from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, default='Unknown')
    info = Column(String, nullable=False, default='Стандартный товар')
    cost = Column(Integer, nullable=False, default=0)
    amount = Column(Integer, nullable=False, default=0)
    #Сделать обработчик численных значений


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    date = Column(String, nullable=False)
    status = Column(String, nullable=False)


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)
    order_amount = Column(Integer, nullable=False)