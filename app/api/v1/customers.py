from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID
from app.db.base import get_db
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.schemas import FilterCustomer, Customer, CreateCustomer, UpdateCustomer, DeleteCustomer, ListCustomer
from app.models.models import Customer as CustomerDB, Order as OrderDB, Vegetable as VegetableDB
from sqlalchemy import select, func

router = APIRouter()

@router.get('/', response_model=ListCustomer)
async def get_customers(
    min_total_quantity: Optional[int] = None,
    vegetable_type_id: Optional[UUID] = None,
    limit: int = 10,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    Получить отфильтрованный список покупателей
    """
    query = select(CustomerDB).distinct()
    
    if min_total_quantity is not None or vegetable_type_id is not None:
        orders_subquery = select(OrderDB.customer_id)
        
        if vegetable_type_id is not None:
            orders_subquery = orders_subquery.where(
                OrderDB.vegetable_id == vegetable_type_id
            )
        
        if min_total_quantity is not None:
            orders_subquery = orders_subquery.group_by(OrderDB.customer_id).having(
                func.sum(OrderDB.quantity) >= min_total_quantity
            )
        
        query = query.where(CustomerDB.uuid.in_(orders_subquery))

    total_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(total_query)

    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()

    customer_list = [
        Customer(
            uuid=item.uuid,
            full_name=item.full_name,
            date_created=item.date_created
        ) for item in items
    ]

    return ListCustomer(
        items=customer_list,
        total=total or 0,
        limit=limit,
        offset=offset
    )

@router.get('/{customer_id}',response_model=Customer)
async def get_customer(
    customer_id: str,
    db: AsyncSession = Depends(get_db)
    ):
    """
    Получить покупателя по UUID
    """
    result = await db.execute(select(CustomerDB).where(CustomerDB.uuid == customer_id))
    customer = result.scalar_one_or_none()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.post('/',response_model=Customer)
async def create_customer(
    customer: CreateCustomer,
    db: AsyncSession = Depends(get_db)
    ):
    """
    Создать нового покупателя
    """
    new_customer = CustomerDB(
        full_name=customer.full_name
    )
    db.add(new_customer)
    await db.commit() 
    return new_customer

@router.put('/{customer_id}',response_model=Customer)
async def update_customer(
    customer_id: str,
    customer: UpdateCustomer,
    db: AsyncSession = Depends(get_db)
    ):
    """
    Обновить информацию о покупателе
    """
    result = await db.execute(select(CustomerDB).where(CustomerDB.uuid == customer_id))
    customer_in_db = result.scalar_one_or_none()
    if customer_in_db is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    customer_in_db.full_name = customer.full_name
    await db.commit()
    return customer_in_db

@router.delete('/{customer_id}',response_model=DeleteCustomer)
async def delete_customer(
    customer_id: str,
    db: AsyncSession = Depends(get_db)
    ):
    """
    Удалить покупателя по UUID
    """
    result = await db.execute(select(CustomerDB).where(CustomerDB.uuid == customer_id))
    customer_in_db = result.scalar_one_or_none()
    if customer_in_db is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    customer_data = Customer(
        uuid=customer_in_db.uuid,
        full_name=customer_in_db.full_name,
        date_created=customer_in_db.date_created
    )
    await db.delete(customer_in_db)
    await db.commit()
    return DeleteCustomer(message='Customer deleted successfully', deleted_customer=customer_data)
