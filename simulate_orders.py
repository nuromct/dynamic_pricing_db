import time
import random
from database import execute_query
from datetime import datetime

def simulate_live_orders():
    print("[START] Canli Siparis Simulasyonu Baslatildi! (Durdurmak icin Ctrl+C)")
    print("---------------------------------------------------------------")
    
    while True:
        try:
            # 1. Rastgele Kullanıcı ve Ürün Seç
            users = execute_query('SELECT UserID, FullName FROM "User"')
            products = execute_query('SELECT ProductID, Title, CurrentPrice FROM Product WHERE IsActive = TRUE')
            
            if not users or not products:
                print("❌ Yeterli veri yok. Once generate_data.py calistirin.")
                break
                
            user = random.choice(users)
            
            # 1-3 arası ürün sepete ekle
            num_items = random.randint(1, 3)
            selected_products = random.sample(products, num_items)
            
            total_amount = 0
            order_items = []
            
            # 2. Stok Kontrolü ve Hesaplama
            valid_order = True
            for prod in selected_products:
                inv = execute_query('SELECT StockQuantity FROM Inventory WHERE ProductID = %s', (prod['productid'],))
                qty = random.randint(1, 5) # Stok hızlı bitsin diye miktarı artırdık
                
                if not inv or inv[0]['stockquantity'] < qty:
                    valid_order = False # Stok yetersiz
                    break
                    
                total_amount += float(prod['currentprice']) * qty
                order_items.append({'id': prod['productid'], 'qty': qty, 'price': prod['currentprice'], 'title': prod['title']})
            
            if not valid_order:
                continue # Bu siparişi pas geç, yenisini dene
                
            # Adres oluştur (User tablosunda adres olmadığı için)
            cities = ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya"]
            districts = ["Merkez", "Cankaya", "Kadikoy", "Besiktas", "Konak"]
            fake_address = f"{random.choice(districts)} Mah. {random.randint(1, 100)}. Sok. No:{random.randint(1, 50)}, {random.choice(cities)}"

            # 3. Siparişi Oluştur
            res = execute_query("""
                INSERT INTO "Order" (UserID, OrderDate, Status, TotalAmount, ShippingAddress)
                VALUES (%s, NOW(), 'completed', %s, %s)
                RETURNING OrderID
            """, (user['userid'], total_amount, fake_address))
            
            order_id = res[0]['orderid']
            
            # 4. Kalemleri Ekle ve Stoğu Düşür
            product_names = []
            for item in order_items:
                execute_query("""
                    INSERT INTO OrderItem (OrderID, ProductID, Quantity, UnitPrice)
                    VALUES (%s, %s, %s, %s)
                """, (order_id, item['id'], item['qty'], item['price']), fetch=False)
                
                # Stoğu düşür (Low Stock Trigger)
                execute_query("""
                    UPDATE Inventory 
                    SET StockQuantity = StockQuantity - %s, LastRestockDate = CURRENT_DATE
                    WHERE ProductID = %s
                """, (item['qty'], item['id']), fetch=False)
                
                product_names.append(item['title'])

            # ==========================================
            # STOK YENILEME (RESTOCK) - FIYAT DUSUSU ICIN
            # ==========================================
            if random.random() < 0.4: # %40 ihtimalle stok ekle
                restock_prod = random.choice(products)
                restock_qty = random.randint(50, 100) # Yuksek stok limiti (100) gecsin diye bol ekle
                
                # Mevcut stogu al
                curr_stock = execute_query('SELECT StockQuantity FROM Inventory WHERE ProductID = %s', (restock_prod['productid'],))
                if curr_stock:
                    # Stogu artir (High Stock Trigger calissin)
                    execute_query("""
                        UPDATE Inventory 
                        SET StockQuantity = StockQuantity + %s, LastRestockDate = CURRENT_DATE
                        WHERE ProductID = %s
                    """, (restock_qty, restock_prod['productid']), fetch=False)
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] [INFO] DEPOYA MAL GELDI: {restock_prod['title']} (+{restock_qty} adet)")
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [OK] Siparis #{order_id} olusturuldu! Tutar: {total_amount:.2f} TL")
            print(f"   Musteri: {user['fullname']}")
            print(f"   Urunler: {', '.join(product_names)}")
            
            # 5. Bekle (HIZLI MOD)
            wait_time = random.uniform(0.1, 0.5)
            time.sleep(wait_time)
            
        except KeyboardInterrupt:
            print("\n[STOP] Simulasyon durduruldu.")
            break
        except Exception as e:
            print(f"[ERROR] Hata: {e}")
            time.sleep(2)

if __name__ == "__main__":
    simulate_live_orders()
