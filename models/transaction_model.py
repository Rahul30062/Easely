from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from db_init import Base

class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    psp = Column(String, nullable=False) 
    razorpay_order_id = Column(String, nullable=False)  
    status = Column(String, nullable=False)  
    order_id = Column(String, ForeignKey('orders.order_id'))

    order = relationship("Order", back_populates="transactions")
