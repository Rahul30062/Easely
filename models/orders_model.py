from sqlalchemy import Column, String, Integer,ForeignKey
from sqlalchemy.orm import relationship
from db_init import Base

class Order(Base):
    __tablename__ = 'orders'
    
    order_id = Column(String, unique=True,primary_key= True, nullable=False)
    amount = Column(Integer, nullable=False)
    currency = Column(String, nullable=False)
    status = Column(String, default='pending')  
    merchant_id = Column(Integer, ForeignKey('merchants.id'))

    merchant = relationship("Merchant", back_populates="orders")
    transactions = relationship("Transaction", back_populates="order")
