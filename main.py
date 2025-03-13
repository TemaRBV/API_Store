from fastapi import Depends, FastAPI, Body
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:password@localhost:5432/postgres"
engine = create_engine(SQLALCHEMY_DATABASE_URL)


class Base(DeclarativeBase): pass


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


# создаем таблицы
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autoflush=False, bind=engine)

app = FastAPI()


# определяем зависимость
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def main():
    return FileResponse("public/home.html")


@app.get("/product")
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()


@app.post("/product")
def create_products(data=Body(), db: Session = Depends(get_db)):
    product = Product(name=data["name"], info=data["info"], cost=data["cost"], amount=data["amount"])
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


#переход на страницу с изменением товара
@app.get("/product/edit")
def edit_product():
    return FileResponse("public/edit.html")


# получаем пользователя по id
@app.get("/product/{id}")
def get_product(id, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == id).first()
    if product is None:
        return JSONResponse(status_code=404, content={"message": "Товар не найден"})
    return product


@app.put("/product/{id}")
def edit_products(id, data=Body(), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == id).first()
    if product is None:
        return JSONResponse(status_code=404, content={"message": "Товар не найден"})
    product.name = data["name"]
    product.info = data["info"]
    product.cost = data["cost"]
    product.amount = data["amount"]
    db.commit()
    db.refresh(product)
    return product


# удаляем пользователя по id
@app.delete("/product/{id}")
def delete_product(id, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == id).first()
    if product is None:
        return JSONResponse(status_code=404, content={"message": "Товар не найден"})

    db.delete(product)
    db.commit()
    return product


#переход на страницу с созданием заказа
@app.get("/orders/new")
def create_order():
    return FileResponse("public/order.html")


@app.get("/orders/list")
def show_order():
    return FileResponse("public/orders.html")


@app.get("/orders")
def get_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()


@app.post("/orders")
def new_order(data=Body(), db: Session = Depends(get_db)):
    product_id = data["id"]
    request_amount = data["amount"]
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return JSONResponse(status_code=404, content={"message": "Такого товара не существует"})
    product_amount = product.amount
    if request_amount > product_amount:
        return JSONResponse(status_code=400, content={"message": "Необходимого количества нет на складе"})
    order = Order(date=data["date"], status="В процессе")
    db.add(order)
    db.commit()
    order_id = order.id
    order_item = OrderItem(order_id=order_id, product_id=product_id, order_amount=request_amount)
    db.add(order_item)
    product.amount = product_amount - request_amount
    db.commit()
    return order_item


@app.get("/orders/{id}")
def get_order(id, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == id).first()
    if order is None:
        return JSONResponse(status_code=404, content={"message": "Заказ не найден"})
    order_item = db.query(OrderItem).filter(OrderItem.order_id == id).first()
    order_amount = order_item.order_amount
    product_id = order_item.product_id
    product = db.query(Product).filter(Product.id == product_id).first()
    name = product.name
    db.commit()

    return {"name": name, "amount": order_amount}


@app.patch("/orders/{id}/status")
def get_orders(id, data=Body(), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == id).first()
    order.status = data["status"]
    db.commit()
    return order
