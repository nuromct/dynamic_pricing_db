import time
import random
from database import execute_query
from datetime import datetime

def simulate_live_orders():
    print("[START] Live Order Simulation Started! (Press Ctrl+C to stop)")
    print("---------------------------------------------------------------")
    
    while True:
        try:
            users = execute_query('SELECT UserID, FullName FROM "User"')
            products = execute_query('SELECT ProductID, Title, CurrentPrice FROM Product WHERE IsActive = TRUE')
            
            if not users or not products:
                print("❌ Not enough data. Run generate_data.py first.")
                break
                
            user = random.choice(users)
            
            num_items = random.randint(1, 3)
            selected_products = random.sample(products, num_items)
            
            total_amount = 0
            order_items = []
            
            valid_order = True
            for prod in selected_products:
                inv = execute_query('SELECT StockQuantity FROM Inventory WHERE ProductID = %s', (prod['productid'],))
                qty = random.randint(1, 5) 
                
                if not inv or inv[0]['stockquantity'] < qty:
                    valid_order = False 
                    break
                    
                total_amount += float(prod['currentprice']) * qty
                order_items.append({'id': prod['productid'], 'qty': qty, 'price': prod['currentprice'], 'title': prod['title']})
            
            if not valid_order:
                continue 
                
            cities = ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya"]
            districts = ["Merkez", "Cankaya", "Kadikoy", "Besiktas", "Konak"]
            fake_address = f"{random.choice(districts)} Mah. {random.randint(1, 100)}. Sok. No:{random.randint(1, 50)}, {random.choice(cities)}"

            res = execute_query("""
                INSERT INTO "Order" (UserID, OrderDate, Status, TotalAmount, ShippingAddress)
                VALUES (%s, NOW(), 'completed', %s, %s)
                RETURNING OrderID
            """, (user['userid'], total_amount, fake_address))
            
            order_id = res[0]['orderid']
            
            product_names = []
            for item in order_items:
                execute_query("""
                    INSERT INTO OrderItem (OrderID, ProductID, Quantity, UnitPrice)
                    VALUES (%s, %s, %s, %s)
                """, (order_id, item['id'], item['qty'], item['price']), fetch=False)
                
                execute_query("""
                    UPDATE Inventory 
                    SET StockQuantity = StockQuantity - %s, LastRestockDate = CURRENT_DATE
                    WHERE ProductID = %s
                """, (item['qty'], item['id']), fetch=False)
                
                product_names.append(item['title'])

            if random.random() < 0.4: 
                restock_prod = random.choice(products)
                restock_qty = random.randint(50, 100) 
                
                curr_stock = execute_query('SELECT StockQuantity FROM Inventory WHERE ProductID = %s', (restock_prod['productid'],))
                if curr_stock:
                    execute_query("""
                        UPDATE Inventory 
                        SET StockQuantity = StockQuantity + %s, LastRestockDate = CURRENT_DATE
                        WHERE ProductID = %s
                    """, (restock_qty, restock_prod['productid']), fetch=False)
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] [INFO] STOCK ARRIVED AT WAREHOUSE: {restock_prod['title']} (+{restock_qty} items)")
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [OK] Order #{order_id} created! Amount: {total_amount:.2f} TL")
            print(f"   Customer: {user['fullname']}")
            print(f"   Products: {', '.join(product_names)}")
            
            wait_time = random.uniform(0.1, 0.5)
            time.sleep(wait_time)
            
        except KeyboardInterrupt:
            print("\n[STOP] Simulation stopped.")
            break
        except Exception as e:
            print(f"[ERROR] Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    simulate_live_orders()
