from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from db_init import Base

class Credential(Base):
    __tablename__ = 'Credentials'
    
    id = Column(Integer, primary_key=True)
    access_key = Column(String, nullable=False, unique=True)
    secret_key = Column(String, nullable=False, unique=True)
    merchant_id = Column(Integer, ForeignKey('merchants.id'))  
    
    merchant = relationship("Merchant", back_populates="credentials")
