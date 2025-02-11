from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Product(Base):
    __tablename__ = "m_product_adachi"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    price = Column(Integer, nullable=False)

class Transaction(Base):
    __tablename__ = "transactions_adachi"
    id = Column(Integer, primary_key=True, index=True)
    total = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)

class TransactionDetail(Base):
    __tablename__ = "transaction_details_adachi"
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions_adachi.id"), nullable=False)
    code = Column(String(50))
    name = Column(String(255))
    price = Column(Integer)
