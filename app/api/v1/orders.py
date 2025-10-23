from fastapi import APIRouter, Depends, HTTPException
from app.schemas.schemas import ListOrder, CreateOrder, UpdateOrder, Order,DeleteOrder,FullOrder, Customer, Vegetable
from app.models.models import Order as OrderDB, Customer as CustomerDB, Vegetable as VegetableDB
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import get_db
from sqlalchemy import select

router = APIRouter()

@router.get('/',response_model=ListOrder)
async def get_orders(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
    ):
    """
    Получить список всех заказов
    """
    result = await db.execute(select(OrderDB).offset(skip).limit(limit))
    items = result.scalars().all()
    total = len(items)
    order_list = [
        Order(
            uuid=item.uuid,
            vegetable_id=item.vegetable_id,
            customer_id=item.customer_id,
            quantity=item.quantity
        ) for item in items
    ]
    return ListOrder(
        items=order_list,
        total=total,
        limit=limit,
        offset=skip
    )

@router.get('/{order_id}',response_model=Order)
async def get_order(
    order_id: str,
    db: AsyncSession = Depends(get_db)
    ):
    """
    Получить заказ по UUID
    """
    result = await db.execute(select(OrderDB).where(OrderDB.uuid == order_id))
    order = result.scalar_one_or_none()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


"""

FullOrder
{
        uuid: order.uuid,
        vegetable_id: order.vegetable_id,
        customer_id: order.customer_id,
        quantity: order.quantity,
        customer: {
            uuid: customer.uuid,
            full_name: customer.full_name,
            date_created: customer.date_created
        },
        vegetable: {
            uuid: vegetable.uuid,
            title: vegetable.title,
            weight: vegetable.weight,
            price: vegetable.price,
            length: vegetable.length
        }
}
"""
@router.post('/',response_model=Order) 
async def create_order(
    order: CreateOrder,
    db: AsyncSession = Depends(get_db)
    ):
    """
    Создать новоый заказ
    """

    # проверка на существование в бд.  так же можно использовать для FullOrder 
    customer = await db.execute(select(CustomerDB).where(CustomerDB.uuid == order.customer_id))
    customer = customer.scalar_one_or_none()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    vegetable = await db.execute(select(VegetableDB).where(VegetableDB.uuid == order.vegetable_id))
    vegetable = vegetable.scalar_one_or_none()
    if vegetable is None:
        raise HTTPException(status_code=404, detail="Vegetable not found")
    
    new_order = OrderDB(
        vegetable_id = order.vegetable_id,
        customer_id = order.customer_id,
        quantity = order.quantity
    )
    db.add(new_order)
    await db.commit() 
    return new_order
    """
    return FullOrder(
        uuid=new_order.uuid,
        vegetable_id=new_order.vegetable_id,
        customer_id=new_order.customer_id,
        quantity=new_order.quantity,
        customer=Customer(
            uuid=customer.uuid,
            full_name=customer.full_name,
            date_created=customer.date_created
            ),
        vegetable=Vegetable(
            uuid=vegetable.uuid,
            title=vegetable.title,
            weight=vegetable.weight,
            price=vegetable.price,
            length=vegetable.length
            )
        )
    """

@router.put('/{order_id}',response_model=Order)
async def update_order(
    order_id: str,
    order: UpdateOrder,
    db: AsyncSession = Depends(get_db)
    ):
    """
    Обновить информацию о заказе
    """
    result = await db.execute(select(OrderDB).where(OrderDB.uuid == order_id))
    order_in_db = result.scalar_one_or_none()
    if order_in_db is None:
        raise HTTPException(status_code=404, detail="Order not found")

    order_in_db.customer_id = order.customer_id
    order_in_db.vegetable_id = order.vegetable_id
    order_in_db.quantity = order.quantity
    await db.commit()
    return order_in_db

@router.delete("/{order_id}",response_model=DeleteOrder)
async def delete_order(
    order_id: str,
    db: AsyncSession = Depends(get_db)
    ):
    """
    Удалить заказ по UUID
    """
    result = await db.execute(select(OrderDB).where(OrderDB.uuid == order_id))
    order_in_db = result.scalar_one_or_none()
    if order_in_db is None:
        raise HTTPException(status_code=404, detail="Order not found")
    order_data = Order(
        uuid=order_in_db.uuid,
        customer_id = order_in_db.customer_id,
        vegetable_id = order_in_db.vegetable_id,
        quantity = order_in_db.quantity
    )
    await db.delete(order_in_db)
    await db.commit()
    return DeleteOrder(message="Order deleted successfully",deleted_order=order_data)


