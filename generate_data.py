
"""
MASSIVE DUMMY DATA GENERATOR
----------------------------
This script populates the database with test data:
- 50 Users
- 10 Suppliers
- 10 Categories
- 100 Products (and Inventory)
- 200 Orders
"""
import random
from faker import Faker
from database import execute_query, get_db_connection
import psycopg2

fake = Faker('tr_TR') 

def clear_database():
    """Clear existing data (optional)"""
    print("[INFO] Cleaning old data...")
    tables = ["OrderItem", "\"Order\"", "PriceHistory", "Inventory", "Product", "Supplier", "Category", "\"User\""]
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        for table in tables:
            cur.execute(f'TRUNCATE TABLE {table} CASCADE;')
        conn.commit()
        print("[OK] Database cleaned.")
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        conn.rollback()
    finally:
        conn.close()

def generate_users(n=50):
    print(f"[INFO] {n} creating users...")
    roles = ['customer', 'customer', 'customer', 'customer', 'seller']
    for _ in range(n):
        execute_query("""
            INSERT INTO "User" (FullName, Email, PasswordHash, Role, PhoneNumber)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            fake.name(),
            fake.unique.email(),
            fake.sha256(),
            random.choice(roles),
            fake.phone_number()[:20]
        ), fetch=False)

def generate_suppliers(n=10):
    print(f"[INFO] {n} creating suppliers...")
    for _ in range(n):
        execute_query("""
            INSERT INTO Supplier (CompanyName, ContactEmail, TaxNumber, Address)
            VALUES (%s, %s, %s, %s)
        """, (
            fake.company(),
            fake.company_email(),
            fake.numerify('##########'),
            fake.address()
        ), fetch=False)

def generate_categories():
    print("[INFO] creating categories...")
    categories = [
        ('Electronics', 'Phone, computer, tablet'),
        ('Clothing', 'Men, women, kids clothing'),
        ('Home & Living', 'Furniture, decoration'),
        ('Sports & Outdoor', 'Sports equipment, camping gear'),
        ('Cosmetics', 'Perfume, makeup, care'),
        ('Books', 'Novel, education, history'),
        ('Toys', 'Educational toys, figures'),
        ('Automotive', 'Car care, accessories'),
        ('Pet Shop', 'Cat, dog food'),
        ('Supermarket', 'Food, cleaning')
    ]
    for name, desc in categories:
        execute_query("""
            INSERT INTO Category (CategoryName, Description)
            VALUES (%s, %s)
        """, (name, desc), fetch=False)

def generate_products(n=100):
    print(f"[INFO] {n} creating products and inventory...")
    
    cat_ids = [r['categoryid'] for r in execute_query("SELECT CategoryID FROM Category")]
    sup_ids = [r['supplierid'] for r in execute_query("SELECT SupplierID FROM Supplier")]
    
    product_prefixes = ['Super', 'Ultra', 'Pro', 'Max', 'Eco', 'Star']
    product_types = ['Laptop', 'Phone', 'Headphones', 'T-shirt', 'Shoes', 'Bag', 'Table', 'Chair', 'Shampoo', 'Novel']
    
    for _ in range(n):
        base_price = round(random.uniform(50, 20000), 2)
        current_price = base_price * random.uniform(0.9, 1.2) 
        
        title = f"{random.choice(product_prefixes)} {random.choice(product_types)} {fake.numerify('###')}"
        
        res = execute_query("""
            INSERT INTO Product (Title, Description, BasePrice, CurrentPrice, IsActive, CategoryID, SupplierID)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING ProductID
        """, (
            title,
            fake.sentence(),
            base_price,
            current_price,
            True,
            random.choice(cat_ids),
            random.choice(sup_ids)
        ))
        pid = res[0]['productid']
        
        execute_query("""
            INSERT INTO Inventory (ProductID, StockQuantity, LowStockThreshold, HighStockThreshold, LastRestockDate)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            pid,
            random.randint(0, 150),
            10,
            100,
            fake.date_between(start_date='-1y', end_date='today')
        ), fetch=False)
        
        if random.random() > 0.5:
            execute_query("""
                INSERT INTO PriceHistory (ProductID, OldPrice, NewPrice, ChangeDate, Reason)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                pid,
                base_price,
                current_price,
                fake.date_between(start_date='-3m', end_date='today'),
                random.choice(['campaign', 'low_stock', 'demand_increase', 'inflation'])
            ), fetch=False)

def generate_orders(n=200):
    print(f"[INFO] {n} creating orders...")
    
    user_ids = [r['userid'] for r in execute_query("SELECT UserID FROM \"User\"")]
    product_ids = [r['productid'] for r in execute_query("SELECT ProductID FROM Product")]
    
    for _ in range(n):
        order_date = fake.date_time_between(start_date='-1y', end_date='now')
        user_id = random.choice(user_ids)
        
        res = execute_query("""
            INSERT INTO "Order" (UserID, OrderDate, Status, TotalAmount, ShippingAddress)
            VALUES (%s, %s, %s, 0, %s) RETURNING OrderID
        """, (
            user_id,
            order_date,
            random.choice(['completed', 'completed', 'completed', 'pending', 'cancelled']),
            fake.address()
        ))
        order_id = res[0]['orderid']
        
        total_amount = 0
        num_items = random.randint(1, 5)
        selected_products = random.sample(product_ids, num_items)
        
        for pid in selected_products:
            price_row = execute_query("SELECT CurrentPrice FROM Product WHERE ProductID = %s", (pid,))
            price = float(price_row[0]['currentprice'])
            qty = random.randint(1, 3)
            
            execute_query("""
                INSERT INTO OrderItem (OrderID, ProductID, Quantity, UnitPrice)
                VALUES (%s, %s, %s, %s)
            """, (order_id, pid, qty, price), fetch=False)
            
            total_amount += price * qty
            
            execute_query("UPDATE Inventory SET StockQuantity = GREATEST(0, StockQuantity - %s) WHERE ProductID = %s", (qty, pid), fetch=False)
            
        execute_query("UPDATE \"Order\" SET TotalAmount = %s WHERE OrderID = %s", (total_amount, order_id), fetch=False)

if __name__ == "__main__":
    print("[INFO] Starting automatic data generation...")
    clear_database()
    generate_users(50)
    generate_suppliers(10)
    generate_categories()
    generate_products(100)
    generate_orders(200)
    print("[SUCCESS] All data successfully created!")
