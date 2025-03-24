from fastapi import Depends, Body, APIRouter
from fastapi.responses import JSONResponse, FileResponse

from sqlalchemy.orm import Session

from models import Product, Order, OrderItem

from db_connection import get_db


router = APIRouter()


# домашняя страница
@router.get("/")
def main():
    return FileResponse("public/home.html")


@router.get("/product")
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()


@router.post("/product")
def create_products(data=Body(), db: Session = Depends(get_db)):
    product = Product(name=data["name"], info=data["info"], cost=data["cost"], amount=data["amount"])
    db.add(product)
    return product


#переход на страницу с изменением товара
@router.get("/product/edit")
def edit_product():
    return FileResponse("public/edit.html")


# получаем пользователя по id
@router.get("/product/{id}")
def get_product(id, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == id).first()
    if product is None:
        return JSONResponse(status_code=404, content={"message": "Товар не найден"})
    return product


@router.put("/product/{id}")
def edit_products(id, data=Body(), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == id).first()
    if product is None:
        return JSONResponse(status_code=404, content={"message": "Товар не найден"})
    product.name = data["name"]
    product.info = data["info"]
    product.cost = data["cost"]
    product.amount = data["amount"]
    return product


# удаляем пользователя по id
@router.delete("/product/{id}")
def delete_product(id, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == id).first()
    if product is None:
        return JSONResponse(status_code=404, content={"message": "Товар не найден"})
    db.delete(product)
    return product


#переход на страницу с созданием заказа
@router.get("/orders/new")
def create_order():
    return FileResponse("public/order.html")


@router.get("/orders/list")
def show_order():
    return FileResponse("public/orders.html")


@router.get("/orders")
def get_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()


@router.delete("/orders")
def del_orders(db: Session = Depends(get_db)):
    db.query(Order).delete()
    return {"message": "Item deleted successfully"}


@router.post("/orders")
def new_order(order_id=None, data=Body(), db: Session = Depends(get_db)):
    product_id = data["id"]
    request_amount = data["amount"]
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return JSONResponse(status_code=404, content={"message": "Такого товара не существует"})
    product_amount = product.amount
    if request_amount > product_amount:
        return JSONResponse(status_code=400, content={"message": "Необходимого количества нет на складе"})
    if not order_id:
        order = Order(status="В процессе")
        db.add(order)
        db.flush()  # Это отправит изменения в базу данных, но не зафиксирует их
        order_id = order.id
        order_item = OrderItem(order_id=order_id, product_id=product_id, order_amount=request_amount)
        db.add(order_item)
        product.amount = product_amount - request_amount
        return order_item
    else:
        query = db.query(OrderItem).filter(OrderItem.order_id == order_id)
        double_item = query.filter(OrderItem.product_id == product_id).first()
        if double_item:
            return JSONResponse(status_code=400, content={"message": "Вы добавляете уже существующий товар. Для "
                                                                     "заказа этого товара создайте новый заказ"})
        else:
            order_item = OrderItem(order_id=order_id, product_id=product_id, order_amount=request_amount)
            db.add(order_item)
            product.amount = product_amount - request_amount
            return order_item


@router.get("/orders/{id}")
def get_order(id, db: Session = Depends(get_db)):
    orders = db.query(OrderItem).filter(OrderItem.order_id == id).all()
    if orders is None:
        return JSONResponse(status_code=404, content={"message": "Заказы не найдены"})
    return orders


@router.patch("/orders/{id}/status")
def get_orders(id, data=Body(), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == id).first()
    order.status = data["status"]
    return order
