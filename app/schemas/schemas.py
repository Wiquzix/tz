from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


# заказчик  
class BaseCustomer(BaseModel):
    full_name: str 

class CreateCustomer(BaseCustomer):
    pass 

class UpdateCustomer(BaseCustomer):
    pass

class Customer(BaseCustomer):
    uuid: UUID
    date_created: datetime

class DeleteCustomer(BaseModel):
    message: str
    deleted_customer: Customer

class ListCustomer(BaseModel):
    items: list[Customer]
    total: int
    limit: int
    offset: int

class FilterCustomer(BaseModel):
    min_total_quantity: Optional[int] = None
    vegetable_type_id: Optional[UUID] = None
    limit: int = 10
    offset: int = 0

class ListCustomer(BaseModel):
    items: list[Customer]
    total: int
    limit: int
    offset: int
# овощи

class BaseVegetable(BaseModel):
    title: str
    weight: int
    price: int 
    length: int

class CreateVegetable(BaseVegetable):
    pass

class UpdateVegetable(BaseVegetable):
    pass

class Vegetable(BaseVegetable):
    uuid: UUID

class DeleteVegetable(BaseModel):
    message: str
    deleted_vegetable: Vegetable

class ListVegetable(BaseModel):
    items: list[Vegetable]
    total: int
    limit: int
    offset: int

# заказы

class BaseOrder(BaseModel):
    vegetable_id: UUID
    customer_id: UUID
    quantity: int

class CreateOrder(BaseOrder):
    pass 

class UpdateOrder(BaseOrder):
    pass

class Order(BaseOrder):
    uuid: UUID

class FullOrder(BaseOrder):
    uuid: UUID
    customer: Customer
    vegetable: Vegetable

class ListOrder(BaseModel):
    items: list[Order]
    total: int
    limit: int
    offset: int

class DeleteOrder(BaseModel):
    message: str
    deleted_order: Order

