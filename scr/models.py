from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    info = Column(String)
    cost = Column(Integer)
    amount = Column(Integer)
    #Сделать обработчик численных значений


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    date = Column(String)
    status = Column(String)


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer)
    product_id = Column(Integer)
    order_amount = Column(Integer)