import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_models import Product, Supplier, Purchase, Sale

# Load environment variables from .env file
load_dotenv()

# Configuration: Database Connection
db_user = os.getenv("POSTGRES_USER")
db_password = os.getenv("POSTGRES_PASSWORD")
db_name = os.getenv("POSTGRES_DB")

DATABASE_URL = f"postgresql://{db_user}:{db_password}@localhost:5432/{db_name}"

# Create Database Engine
engine = create_engine(DATABASE_URL)

# Create a new session
Session = sessionmaker(bind=engine)
session = Session()

# Fetch and print all data from the Product table
products = session.query(Product).all()
print("Products:")
for product in products:
    print(f"ID: {product.id}, Name: {product.name}, Category: {product.category}, Description: {product.description}")

# Fetch and print all data from the Supplier table
suppliers = session.query(Supplier).all()
print("\nSuppliers:")
for supplier in suppliers:
    print(f"ID: {supplier.id}, Name: {supplier.name}, City: {supplier.city}, Address: {supplier.address}")

# Fetch and print all data from the Purchase table
purchases = session.query(Purchase).all()
print("\nPurchases:")
for purchase in purchases:
    print(f"ID: {purchase.id}, Product ID: {purchase.product_id}, Supplier ID: {purchase.supplier_id}, Purchase Date: {purchase.purchase_date}, Quantity: {purchase.quantity}, Unit Cost: {purchase.unit_cost}")

# Fetch and print all data from the Sale table
sales = session.query(Sale).all()
print("\nSales:")
for sale in sales:
    print(f"ID: {sale.id}, Product ID: {sale.product_id}, Sale Date: {sale.sale_date}, Quantity: {sale.quantity}, Unit Price: {sale.unit_price}")

# Close the session
session.close()
