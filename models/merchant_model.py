from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from db_init import Base

class Merchant(Base):
    __tablename__ = 'merchants'
    
    id = Column(Integer, primary_key=True)
    merchant_name = Column(String, nullable=False)
    merchant_email = Column(String, nullable=False, unique=True)
    merchant_password = Column(String, nullable=False, unique=True)
    
    credentials = relationship("Credential", back_populates="merchant", uselist=False)
    orders = relationship("Order", back_populates="merchant")
