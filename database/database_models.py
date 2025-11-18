import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Text, Date, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Load environment variables from .env file
load_dotenv()

# Configuration: Database Connection
db_user = os.getenv("POSTGRES_USER")
db_password = os.getenv("POSTGRES_PASSWORD")
db_name = os.getenv("POSTGRES_DB")

DATABASE_URL = f"postgresql://{db_user}:{db_password}@localhost:5432/{db_name}"

# Base class for ORM models
Base = declarative_base()

# Product Model
class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String)
    description = Column(Text)

    purchases = relationship('Purchase', back_populates='product')
    sales = relationship('Sale', back_populates='product')

# Supplier Model
class Supplier(Base):
    __tablename__ = 'suppliers'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    city = Column(String)
    address = Column(String)

    purchases = relationship('Purchase', back_populates='supplier')

# Purchase Model
class Purchase(Base):
    __tablename__ = 'purchases'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    purchase_date = Column(Date)
    quantity = Column(Integer)
    unit_cost = Column(Float)

    product = relationship('Product', back_populates='purchases')
    supplier = relationship('Supplier', back_populates='purchases')

# Sale Model
class Sale(Base):
    __tablename__ = 'sales'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    sale_date = Column(Date)
    quantity = Column(Integer)
    unit_price = Column(Float)

    product = relationship('Product', back_populates='sales')

# Create Database Engine
engine = create_engine(DATABASE_URL)

# Create all tables
Base.metadata.create_all(engine)

print("Models defined and tables created.")
