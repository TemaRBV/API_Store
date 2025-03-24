from fastapi import Depends, Body, APIRouter
from fastapi.responses import JSONResponse, FileResponse

from sqlalchemy import delete, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models import Product, Order, OrderItem

from db_connection import get_db


router = APIRouter()


# домашняя страница
@router.get("/")
def main():
    return FileResponse("public/home.html")


@router.get("/product")
async def get_products(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product))
    return result.scalars().all()


@router.post("/product")
async def create_products(data=Body(), db: AsyncSession = Depends(get_db)):
    product = Product(name=data["name"], info=data["info"], cost=data["cost"], amount=data["amount"])
    db.add(product)
    return product


#переход на страницу с изменением товара
@router.get("/product/edit")
def edit_product():
    return FileResponse("public/edit.html")


# получаем пользователя по id
@router.get("/product/{id}")
async def get_product(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == id))
    product = result.scalars().first()
    if product is None:
        return JSONResponse(status_code=404, content={"message": "Товар не найден"})
    return product


@router.put("/product/{id}")
async def edit_products(id: int, data=Body(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == id))
    product = result.scalars().first()
    if product is None:
        return JSONResponse(status_code=404, content={"message": "Товар не найден"})
    product.name = data["name"]
    product.info = data["info"]
    product.cost = data["cost"]
    product.amount = data["amount"]
    return product


# удаляем товар по id
@router.delete("/product/{id}")
async def delete_product(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == id))
    product = result.scalars().first()
    if product is None:
        return JSONResponse(status_code=404, content={"message": "Товар не найден"})
    item_result = await db.execute(select(OrderItem).where(OrderItem.product_id == id))
    item = item_result.scalars().all()
    if item:
        return JSONResponse(status_code=400, content={"message": "Вы не можете удалить товар пока он есть в списках "
                                                                 "заказов"})
    await db.delete(product)
    return JSONResponse(status_code=204, content={"message": "Товар успешно удален"})


#переход на страницу с созданием заказа
@router.get("/orders/new")
def create_order():
    return FileResponse("public/order.html")


#переход на страницу со списком заказов
@router.get("/orders/list")
def show_order():
    return FileResponse("public/orders.html")


@router.get("/orders")
async def get_orders(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Order))
    return result.scalars().all()


@router.delete("/orders")
async def del_orders(db: AsyncSession = Depends(get_db)):
    await db.execute(delete(Order))
    await db.execute(delete(OrderItem))
    return {"message": "Item deleted successfully"}


@router.post("/orders")
async def new_order(order_id: int = None, data=Body(), db: AsyncSession = Depends(get_db)):
    product_id = int(data["id"])
    request_amount = data["amount"]
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalars().first()
    if not product:
        return JSONResponse(status_code=404, content={"message": "Такого товара не существует"})
    product_amount = product.amount
    if request_amount > product_amount:
        return JSONResponse(status_code=400, content={"message": "Необходимого количества нет на складе"})
    if not order_id:
        order = Order(status="В процессе")
        db.add(order)
        await db.flush()  # Это отправит изменения в базу данных, но не зафиксирует их
        order_id = order.id
        order_item = OrderItem(order_id=order_id, product_id=product_id, order_amount=request_amount)
        db.add(order_item)
        product.amount = product_amount - request_amount
        return order_item
    else:
        condition = and_(OrderItem.order_id == order_id, OrderItem.product_id == product_id)
        result_item = await db.execute(select(OrderItem).where(condition))
        double_item = result_item.scalars().first()
        if double_item:
            return JSONResponse(status_code=400, content={"message": "Вы добавляете уже существующий товар. Для "
                                                                     "заказа этого товара создайте новый заказ"})
        else:
            order_item = OrderItem(order_id=order_id, product_id=product_id, order_amount=request_amount)
            db.add(order_item)
            product.amount = product_amount - request_amount
            return order_item


@router.get("/orders/{id}")
async def get_order(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(OrderItem).where(OrderItem.order_id == id))
    orders = result.scalars().all()
    if orders is None:
        return JSONResponse(status_code=404, content={"message": "Заказы не найдены"})
    return orders


@router.patch("/orders/{id}/status")
async def get_orders(id: int, data=Body(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Order).where(Order.id == id))
    order = result.scalars().first()
    order.status = data["status"]
    return order
