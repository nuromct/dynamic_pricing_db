from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from database import execute_query
import os

app = FastAPI(
    title="Dynamic Pricing API",
    description="Dynamic Pricing and Inventory Management System for E-commerce",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

class ProductCreate(BaseModel):
    title: str
    description: Optional[str] = None
    base_price: float
    current_price: float
    is_active: bool = True
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None

class ProductUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    base_price: Optional[float] = None
    current_price: Optional[float] = None
    is_active: Optional[bool] = None
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None

class CategoryCreate(BaseModel):
    category_name: str
    description: Optional[str] = None

class InventoryUpdate(BaseModel):
    stock_quantity: int
    low_stock_threshold: Optional[int] = 10
    high_stock_threshold: Optional[int] = 100

class OrderCreate(BaseModel):
    user_id: int
    shipping_address: str
    items: List[dict] 

class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str
    role: str = "customer"
    phone_number: Optional[str] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    phone_number: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

@app.get("/")
async def root():
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    return {"message": "Dynamic Pricing API", "docs": "/docs"}

@app.get("/store")
async def store():
    if os.path.exists("static/store.html"):
        return FileResponse("static/store.html")
    return {"message": "Store page not found"}

@app.get("/api/products")
async def get_products(
    category_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_stock: Optional[int] = None,
    search: Optional[str] = None
):
    query = """
        SELECT p.*, c.categoryname as category_name, s.companyname as supplier_name, i.stockquantity
        FROM product p
        LEFT JOIN category c ON p.categoryid = c.categoryid
        LEFT JOIN supplier s ON p.supplierid = s.supplierid
        LEFT JOIN inventory i ON p.productid = i.productid
        WHERE 1=1
    """
    params = []
    
    if category_id:
        query += " AND p.categoryid = %s"
        params.append(category_id)
    if is_active is not None:
        query += " AND p.isactive = %s"
        params.append(is_active)
    if min_price:
        query += " AND p.currentprice >= %s"
        params.append(min_price)
    if max_price:
        query += " AND p.currentprice <= %s"
        params.append(max_price)
    if min_stock is not None:
        query += " AND i.stockquantity >= %s"
        params.append(min_stock)
    if search:
        query += " AND (p.title ILIKE %s OR p.description ILIKE %s)"
        params.append(f"%{search}%")
        params.append(f"%{search}%")
    
    query += " ORDER BY p.productid"
    
    products = execute_query(query, tuple(params) if params else None)
    return {"products": products, "count": len(products)}

class CampaignCreate(BaseModel):
    category_id: int
    discount_percentage: float

@app.post("/api/campaigns/apply")
async def apply_campaign(campaign: CampaignCreate):
    products = execute_query("SELECT productid, currentprice FROM product WHERE categoryid = %s", (campaign.category_id,))
    
    if not products:
        return {"message": "No products found in this category"}
        
    count = 0
    for prod in products:
        old_price = float(prod['currentprice'])
        new_price = old_price * (1 - campaign.discount_percentage / 100)
        
        execute_query("UPDATE product SET currentprice = %s WHERE productid = %s", (new_price, prod['productid']), fetch=False)
        
        execute_query("""
            INSERT INTO pricehistory (productid, oldprice, newprice, reason, changedate)
            VALUES (%s, %s, %s, 'campaign', NOW())
        """, (prod['productid'], old_price, new_price), fetch=False)
        
        count += 1
        
    return {"message": f"{count} products discounted by {campaign.discount_percentage}%"}

@app.get("/api/products/{product_id}")
async def get_product(product_id: int):
    query = """
        SELECT p.*, c.categoryname, s.companyname,
               i.stockquantity, i.lowstockthreshold, i.highstockthreshold
        FROM product p
        LEFT JOIN category c ON p.categoryid = c.categoryid
        LEFT JOIN supplier s ON p.supplierid = s.supplierid
        LEFT JOIN inventory i ON p.productid = i.productid
        WHERE p.productid = %s
    """
    result = execute_query(query, (product_id,))
    if not result:
        raise HTTPException(status_code=404, detail="Product not found")
    return result[0]

@app.post("/api/products")
async def create_product(product: ProductCreate):
    query = """
        INSERT INTO product (title, description, baseprice, currentprice, isactive, categoryid, supplierid)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING productid
    """
    result = execute_query(query, (
        product.title, product.description, product.base_price,
        product.current_price, product.is_active, product.category_id, product.supplier_id
    ))
    
    new_product_id = result[0]["productid"]
    
    inventory_query = """
        INSERT INTO inventory (productid, stockquantity, lowstockthreshold, highstockthreshold, lastrestockdate)
        VALUES (%s, 0, 10, 100, CURRENT_DATE)
    """
    execute_query(inventory_query, (new_product_id,), fetch=False)
    
    return {"message": "Product and inventory record created", "product_id": new_product_id}

@app.put("/api/products/{product_id}")
async def update_product(product_id: int, product: ProductUpdate):
    existing = execute_query("SELECT * FROM product WHERE productid = %s", (product_id,))
    if not existing:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.current_price and product.current_price != existing[0]["currentprice"]:
        history_query = """
            INSERT INTO pricehistory (productid, oldprice, newprice, reason)
            VALUES (%s, %s, %s, %s)
        """
        execute_query(history_query, (
            product_id, existing[0]["currentprice"], product.current_price, "manual_update"
        ), fetch=False)
    
    updates = []
    params = []
    if product.title:
        updates.append("title = %s")
        params.append(product.title)
    if product.description:
        updates.append("description = %s")
        params.append(product.description)
    if product.base_price:
        updates.append("baseprice = %s")
        params.append(product.base_price)
    if product.current_price:
        updates.append("currentprice = %s")
        params.append(product.current_price)
    if product.is_active is not None:
        updates.append("isactive = %s")
        params.append(product.is_active)
    
    if updates:
        params.append(product_id)
        query = f"UPDATE product SET {', '.join(updates)} WHERE productid = %s"
        execute_query(query, tuple(params), fetch=False)
    
    return {"message": "Product updated"}

@app.delete("/api/products/{product_id}")
async def delete_product(product_id: int):
    existing = execute_query("SELECT * FROM product WHERE productid = %s", (product_id,))
    if not existing:
        raise HTTPException(status_code=404, detail="Product not found")
    
    execute_query("DELETE FROM orderitem WHERE productid = %s", (product_id,), fetch=False)
    execute_query("DELETE FROM pricehistory WHERE productid = %s", (product_id,), fetch=False)
    execute_query("DELETE FROM inventory WHERE productid = %s", (product_id,), fetch=False)
    
    execute_query("DELETE FROM product WHERE productid = %s", (product_id,), fetch=False)
    return {"message": "Product deleted"}

@app.get("/api/categories")
async def get_categories():
    query = """
        SELECT c.*, COUNT(p.productid) as product_count
        FROM category c
        LEFT JOIN product p ON c.categoryid = p.categoryid
        GROUP BY c.categoryid
        ORDER BY c.categoryid
    """
    return execute_query(query)

@app.post("/api/categories")
async def create_category(category: CategoryCreate):
    query = "INSERT INTO category (categoryname, description) VALUES (%s, %s) RETURNING categoryid"
    result = execute_query(query, (category.category_name, category.description))
    return {"message": "Category created", "category_id": result[0]["categoryid"]}

class SupplierCreate(BaseModel):
    company_name: str
    contact_email: Optional[str] = None
    tax_number: Optional[str] = None
    address: Optional[str] = None

class SupplierUpdate(BaseModel):
    company_name: Optional[str] = None
    contact_email: Optional[str] = None
    tax_number: Optional[str] = None
    address: Optional[str] = None

@app.get("/api/suppliers")
async def get_suppliers():
    query = """
        SELECT s.*, COUNT(p.productid) as product_count
        FROM supplier s
        LEFT JOIN product p ON s.supplierid = p.supplierid
        GROUP BY s.supplierid
        ORDER BY s.supplierid
    """
    return execute_query(query)

@app.get("/api/suppliers/{supplier_id}")
async def get_supplier(supplier_id: int):
    result = execute_query('SELECT * FROM supplier WHERE supplierid = %s', (supplier_id,))
    if not result:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return result[0]

@app.post("/api/suppliers")
async def create_supplier(supplier: SupplierCreate):
    query = """
        INSERT INTO supplier (companyname, contactemail, taxnumber, address)
        VALUES (%s, %s, %s, %s)
        RETURNING supplierid
    """
    result = execute_query(query, (supplier.company_name, supplier.contact_email, supplier.tax_number, supplier.address))
    return {"message": "Supplier created", "supplier_id": result[0]["supplierid"]}

@app.put("/api/suppliers/{supplier_id}")
async def update_supplier(supplier_id: int, supplier: SupplierUpdate):
    existing = execute_query('SELECT * FROM supplier WHERE supplierid = %s', (supplier_id,))
    if not existing:
        raise HTTPException(status_code=404, detail="Supplier not found")
    
    updates = []
    params = []
    
    if supplier.company_name:
        updates.append("companyname = %s")
        params.append(supplier.company_name)
    if supplier.contact_email is not None:
        updates.append("contactemail = %s")
        params.append(supplier.contact_email)
    if supplier.tax_number is not None:
        updates.append("taxnumber = %s")
        params.append(supplier.tax_number)
    if supplier.address is not None:
        updates.append("address = %s")
        params.append(supplier.address)
    
    if updates:
        params.append(supplier_id)
        query = f'UPDATE supplier SET {", ".join(updates)} WHERE supplierid = %s'
        execute_query(query, tuple(params), fetch=False)
    
    return {"message": "Supplier updated"}

@app.delete("/api/suppliers/{supplier_id}")
async def delete_supplier(supplier_id: int):
    execute_query('UPDATE product SET supplierid = NULL WHERE supplierid = %s', (supplier_id,), fetch=False)
    execute_query('DELETE FROM supplier WHERE supplierid = %s', (supplier_id,), fetch=False)
    return {"message": "Supplier deleted"}

@app.get("/api/inventory")
async def get_inventory():
    query = """
        SELECT i.*, p.title, p.currentprice,
               CASE 
                   WHEN i.stockquantity < i.lowstockthreshold THEN 'LOW'
                   WHEN i.stockquantity > i.highstockthreshold THEN 'HIGH'
                   ELSE 'NORMAL'
               END as stock_status
        FROM inventory i
        INNER JOIN product p ON i.productid = p.productid
        ORDER BY i.stockquantity ASC
    """
    return execute_query(query)

@app.get("/api/inventory/low-stock")
async def get_low_stock():
    query = """
        SELECT i.*, p.title, p.currentprice
        FROM inventory i
        INNER JOIN product p ON i.productid = p.productid
        WHERE i.stockquantity < i.lowstockthreshold
        ORDER BY i.stockquantity ASC
    """
    return execute_query(query)

@app.put("/api/inventory/{product_id}")
async def update_inventory(product_id: int, inventory: InventoryUpdate):
    query = """
        UPDATE inventory 
        SET stockquantity = %s, lowstockthreshold = %s, highstockthreshold = %s, lastrestockdate = CURRENT_DATE
        WHERE productid = %s
    """
    result = execute_query(query, (
        inventory.stock_quantity, inventory.low_stock_threshold, 
        inventory.high_stock_threshold, product_id
    ), fetch=False)
    
    if result == 0:
        insert_query = """
            INSERT INTO inventory (productid, stockquantity, lowstockthreshold, highstockthreshold, lastrestockdate)
            VALUES (%s, %s, %s, %s, CURRENT_DATE)
        """
        execute_query(insert_query, (
            product_id, inventory.stock_quantity, 
            inventory.low_stock_threshold, inventory.high_stock_threshold
        ), fetch=False)
    
    return {"message": "Stock updated"}

@app.get("/api/price-history")
async def get_price_history(product_id: Optional[int] = None):
    query = """
        SELECT ph.*, p.title
        FROM pricehistory ph
        INNER JOIN product p ON ph.productid = p.productid
    """
    params = []
    
    if product_id:
        query += " WHERE ph.productid = %s"
        params.append(product_id)
    
    query += " ORDER BY ph.changedate DESC"
    
    return execute_query(query, tuple(params) if params else None)

@app.get("/api/orders")
async def get_orders(user_id: Optional[int] = None, status: Optional[str] = None):
    query = """
        SELECT o.orderid, o.orderdate, o.status, o.totalamount, o.shippingaddress,
               u.fullname as customer_name,
               (SELECT string_agg(p.title || ' x' || oi.quantity, ', ')
                FROM OrderItem oi
                INNER JOIN Product p ON oi.productid = p.productid
                WHERE oi.orderid = o.orderid) as order_items,
               (SELECT string_agg(DISTINCT s.companyname, ', ')
                FROM OrderItem oi
                INNER JOIN Product p ON oi.productid = p.productid
                LEFT JOIN Supplier s ON p.supplierid = s.supplierid
                WHERE oi.orderid = o.orderid AND s.companyname IS NOT NULL) as suppliers
        FROM "Order" o
        INNER JOIN "User" u ON o.userid = u.userid
        WHERE 1=1
    """
    params = []
    
    if user_id:
        query += " AND o.userid = %s"
        params.append(user_id)
    if status:
        query += " AND o.status = %s"
        params.append(status)
    
    query += " ORDER BY o.orderdate DESC"
    
    return execute_query(query, tuple(params) if params else None)

@app.post("/api/orders")
async def create_order(order: OrderCreate):
    total_amount = 0
    valid_items = []
    
    for item in order.items:
        product_id = item.get("product_id")
        quantity = item.get("quantity")
        
        prod_query = """
            SELECT p.currentprice, i.stockquantity 
            FROM product p 
            JOIN inventory i ON p.productid = i.productid 
            WHERE p.productid = %s
        """
        product_data = execute_query(prod_query, (product_id,))
        
        if not product_data:
             raise HTTPException(status_code=404, detail=f"Product ID {product_id} not found")
             
        current_price = product_data[0]["currentprice"]
        stock_quantity = product_data[0]["stockquantity"]
        
        if stock_quantity < quantity:
             raise HTTPException(status_code=400, detail=f"Insufficient stock for Product ID {product_id} (Available: {stock_quantity})")
             
        total_amount += float(current_price) * quantity
        valid_items.append({
            "product_id": product_id,
            "quantity": quantity,
            "unit_price": current_price
        })

    order_query = """
        INSERT INTO "Order" (userid, orderdate, status, totalamount, shippingaddress)
        VALUES (%s, CURRENT_DATE, 'pending', %s, %s)
        RETURNING orderid
    """
    order_result = execute_query(order_query, (order.user_id, total_amount, order.shipping_address))
    new_order_id = order_result[0]["orderid"]
    
    for item in valid_items:
        item_query = """
            INSERT INTO orderitem (orderid, productid, quantity, unitprice)
            VALUES (%s, %s, %s, %s)
        """
        execute_query(item_query, (new_order_id, item["product_id"], item["quantity"], item["unit_price"]), fetch=False)
        
        stock_update_query = """
            UPDATE inventory 
            SET stockquantity = stockquantity - %s, lastrestockdate = CURRENT_DATE
            WHERE productid = %s
        """
        execute_query(stock_update_query, (item["quantity"], item["product_id"]), fetch=False)
        
    return {"message": "Order created", "order_id": new_order_id}

@app.get("/api/orders/{order_id}")
async def get_order(order_id: int):
    order_query = """
        SELECT o.*, u.fullname, u.email
        FROM "Order" o
        INNER JOIN "User" u ON o.userid = u.userid
        WHERE o.orderid = %s
    """
    order = execute_query(order_query, (order_id,))
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    items_query = """
        SELECT oi.*, p.title
        FROM orderitem oi
        INNER JOIN product p ON oi.productid = p.productid
        WHERE oi.orderid = %s
    """
    items = execute_query(items_query, (order_id,))
    
    result = dict(order[0])
    result["items"] = items
    return result

@app.get("/api/users")
async def get_users():
    return execute_query('SELECT userid, fullname, email, role, phonenumber FROM "User" ORDER BY userid')

@app.get("/api/users/{user_id}")
async def get_user(user_id: int):
    result = execute_query('SELECT * FROM "User" WHERE userid = %s', (user_id,))
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return result[0]

@app.post("/api/users")
async def create_user(user: UserCreate):
    import hashlib
    password_hash = hashlib.sha256(user.password.encode()).hexdigest()
    
    query = """
        INSERT INTO "User" (fullname, email, passwordhash, role, phonenumber)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING userid
    """
    try:
        result = execute_query(query, (user.full_name, user.email, password_hash, user.role, user.phone_number))
        return {"message": "User created", "user_id": result[0]["userid"]}
    except Exception as e:
        if "unique" in str(e).lower() and "email" in str(e).lower():
            raise HTTPException(status_code=400, detail="This email address is already registered")
        elif "unique" in str(e).lower() and "phone" in str(e).lower():
            raise HTTPException(status_code=400, detail="This phone number is already registered")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/login")
async def login(credentials: UserLogin):
    import hashlib
    password_hash = hashlib.sha256(credentials.password.encode()).hexdigest()
    
    query = 'SELECT userid, fullname, email, role FROM "User" WHERE email = %s AND passwordhash = %s'
    result = execute_query(query, (credentials.email, password_hash))
    
    if not result:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    return {"message": "Login successful", "user": result[0]}

@app.put("/api/users/{user_id}")
async def update_user(user_id: int, user: UserUpdate):
    existing = execute_query('SELECT * FROM "User" WHERE userid = %s', (user_id,))
    if not existing:
        raise HTTPException(status_code=404, detail="User not found")
    
    updates = []
    params = []
    
    if user.full_name:
        updates.append("fullname = %s")
        params.append(user.full_name)
    if user.email:
        updates.append("email = %s")
        params.append(user.email)
    if user.password:
        import hashlib
        updates.append("passwordhash = %s")
        params.append(hashlib.sha256(user.password.encode()).hexdigest())
    if user.role:
        updates.append("role = %s")
        params.append(user.role)
    if user.phone_number:
        updates.append("phonenumber = %s")
        params.append(user.phone_number)
    
    if updates:
        params.append(user_id)
        query = f'UPDATE "User" SET {", ".join(updates)} WHERE userid = %s'
        execute_query(query, tuple(params), fetch=False)
    
    return {"message": "User updated"}

@app.delete("/api/users/{user_id}")
async def delete_user(user_id: int):
    existing = execute_query('SELECT * FROM "User" WHERE userid = %s', (user_id,))
    if not existing:
        raise HTTPException(status_code=404, detail="User not found")
    
    execute_query('DELETE FROM orderitem WHERE orderid IN (SELECT orderid FROM "Order" WHERE userid = %s)', (user_id,), fetch=False)
    execute_query('DELETE FROM "Order" WHERE userid = %s', (user_id,), fetch=False)
    execute_query('DELETE FROM "User" WHERE userid = %s', (user_id,), fetch=False)
    
    return {"message": "User deleted"}

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    stats = {}
    
    stats["total_products"] = execute_query("SELECT COUNT(*) as count FROM product")[0]["count"]
    
    stats["total_categories"] = execute_query("SELECT COUNT(*) as count FROM category")[0]["count"]
    
    stats["total_orders"] = execute_query('SELECT COUNT(*) as count FROM "Order"')[0]["count"]
    
    revenue = execute_query('SELECT COALESCE(SUM(totalamount), 0) as total FROM "Order" WHERE status = %s', ('completed',))
    stats["total_revenue"] = float(revenue[0]["total"])
    
    low_stock = execute_query("SELECT COUNT(*) as count FROM inventory WHERE stockquantity < lowstockthreshold")
    stats["low_stock_count"] = low_stock[0]["count"]
    
    avg_price = execute_query("SELECT COALESCE(AVG(currentprice), 0) as avg FROM product")
    stats["average_price"] = round(float(avg_price[0]["avg"]), 2)
    
    return stats

@app.get("/api/dashboard/category-distribution")
async def get_category_distribution():
    query = """
        SELECT c.categoryname as name, COUNT(p.productid) as value
        FROM category c
        LEFT JOIN product p ON c.categoryid = p.categoryid
        GROUP BY c.categoryid, c.categoryname
        ORDER BY value DESC
    """
    return execute_query(query)

@app.get("/api/dashboard/price-trends")
async def get_price_trends():
    query = """
        SELECT DATE(changedate) as date, 
               COUNT(*) as changes,
               AVG(newprice - oldprice) as avg_change
        FROM pricehistory
        GROUP BY DATE(changedate)
        ORDER BY date DESC
        LIMIT 30
    """
    return execute_query(query)
