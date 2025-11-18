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

# Sample Data Insertion
# Add Suppliers
supplier1 = Supplier(name='Supplier A', city='City A', address='123 Street A')
supplier2 = Supplier(name='Supplier B', city='City B', address='456 Street B')

session.add(supplier1)
session.add(supplier2)

# Add Products
product1 = Product(name='Product A', category='Category A', description='Description for Product A')
product2 = Product(name='Product B', category='Category B', description='Description for Product B')
product3 = Product(name='Product C', category='Category C', description='Description for Product C')

session.add(product1)
session.add(product2)
session.add(product3)

# Add Purchases
purchase1 = Purchase(product_id=product1.id, supplier_id=supplier1.id, purchase_date='2023-01-01', quantity=10, unit_cost=5.0)
purchase2 = Purchase(product_id=product1.id, supplier_id=supplier2.id, purchase_date='2023-01-05', quantity=20, unit_cost=4.5)
purchase3 = Purchase(product_id=product2.id, supplier_id=supplier1.id, purchase_date='2023-01-10', quantity=15, unit_cost=7.0)

session.add(purchase1)
session.add(purchase2)
session.add(purchase3)

# Add Sales
sale1 = Sale(product_id=product1.id, sale_date='2023-01-02', quantity=5, unit_price=10.0)
sale2 = Sale(product_id=product1.id, sale_date='2023-01-06', quantity=3, unit_price=9.5)
sale3 = Sale(product_id=product2.id, sale_date='2023-01-15', quantity=7, unit_price=12.0)

session.add(sale1)
session.add(sale2)
session.add(sale3)

# Commit the session
session.commit()
session.close()

print("Sample data has been inserted.")
