
from sqlalchemy import Column, String, DateTime, ForeignKey, text,Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Customer(Base):
    __tablename__ = 'customers'

    uuid = Column(UUID(as_uuid=True), primary_key=True, nullable=False, server_default=text("gen_random_uuid()"))
    full_name = Column(String, nullable=False)
    date_created = Column(DateTime, default=datetime.now)

class Vegetable(Base):
    __tablename__ = 'vegetables'

    uuid = Column(UUID(as_uuid=True), primary_key=True, nullable=False, server_default=text("gen_random_uuid()"))
    title = Column(String, nullable=False)
    weight = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    length = Column(Integer, nullable=False)

class Order(Base):
    __tablename__ = 'orders'

    uuid = Column(UUID(as_uuid=True), primary_key=True, nullable=False, server_default=text("gen_random_uuid()"))
    vegetable_id = Column(UUID(as_uuid=True), ForeignKey('vegetables.uuid'), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.uuid'), nullable=False)
    quantity = Column(Integer, nullable=False)

    customer = relationship("Customer", backref="orders")
    vegetable = relationship("Vegetable", backref="orders")


