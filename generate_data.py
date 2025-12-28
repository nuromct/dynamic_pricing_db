"""
MASSIVE DUMMY DATA GENERATOR
----------------------------
Bu script veritabanını test verileriyle doldurur:
- 50 Kullanıcı
- 10 Tedarikçi
- 10 Kategori
- 100 Ürün (ve Envanter)
- 200 Sipariş
"""
import random
from faker import Faker
from database import execute_query, get_db_connection
import psycopg2

fake = Faker('tr_TR')  # Türkçe veri üretimi

def clear_database():
    """Mevcut verileri temizle (opsiyonel)"""
    print("[INFO] Eski veriler temizleniyor...")
    tables = ["OrderItem", "\"Order\"", "PriceHistory", "Inventory", "Product", "Supplier", "Category", "\"User\""]
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        for table in tables:
            cur.execute(f'TRUNCATE TABLE {table} CASCADE;')
        conn.commit()
        print("[OK] Veritabani temizlendi.")
    except Exception as e:
        print(f"[ERROR] Hata: {e}")
        conn.rollback()
    finally:
        conn.close()

def generate_users(n=50):
    print(f"[INFO] {n} kullanici olusturuluyor...")
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
    print(f"[INFO] {n} tedarikci olusturuluyor...")
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
    print("[INFO] Kategoriler olusturuluyor...")
    categories = [
        ('Elektronik', 'Telefon, bilgisayar, tablet'),
        ('Giyim', 'Erkek, kadin, cocuk giyim'),
        ('Ev & Yasam', 'Mobilya, dekorasyon'),
        ('Spor & Outdoor', 'Spor aletleri, kamp malzemeleri'),
        ('Kozmetik', 'Parfum, makyaj, bakim'),
        ('Kitap', 'Roman, egitim, tarih'),
        ('Oyuncak', 'Egitici oyuncaklar, figurler'),
        ('Otomotiv', 'Arac bakim, aksesuar'),
        ('Pet Shop', 'Kedi, kopek mamalari'),
        ('Supermarket', 'Gida, temizlik')
    ]
    for name, desc in categories:
        execute_query("""
            INSERT INTO Category (CategoryName, Description)
            VALUES (%s, %s)
        """, (name, desc), fetch=False)

def generate_products(n=100):
    print(f"[INFO] {n} urun ve stok olusturuluyor...")
    
    # ID'leri al
    cat_ids = [r['categoryid'] for r in execute_query("SELECT CategoryID FROM Category")]
    sup_ids = [r['supplierid'] for r in execute_query("SELECT SupplierID FROM Supplier")]
    
    product_prefixes = ['Super', 'Ultra', 'Pro', 'Max', 'Eco', 'Star']
    product_types = ['Laptop', 'Telefon', 'Kulaklik', 'Tisort', 'Ayakkabi', 'Canta', 'Masa', 'Sandalye', 'Sampuan', 'Roman']
    
    for _ in range(n):
        base_price = round(random.uniform(50, 20000), 2)
        current_price = base_price * random.uniform(0.9, 1.2)  # %10 indirim veya %20 zamlı
        
        title = f"{random.choice(product_prefixes)} {random.choice(product_types)} {fake.numerify('###')}"
        
        # Ürün ekle
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
        
        # Stok ekle
        execute_query("""
            INSERT INTO Inventory (ProductID, StockQuantity, LowStockThreshold, HighStockThreshold, LastRestockDate)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            pid,
            random.randint(0, 150),  # 0 stoklu ürünler de olsun
            10,
            100,
            fake.date_between(start_date='-1y', end_date='today')
        ), fetch=False)
        
        # Fiyat geçmişi (bazı ürünler için)
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
    print(f"[INFO] {n} siparis olusturuluyor...")
    
    user_ids = [r['userid'] for r in execute_query("SELECT UserID FROM \"User\"")]
    product_ids = [r['productid'] for r in execute_query("SELECT ProductID FROM Product")]
    
    for _ in range(n):
        order_date = fake.date_time_between(start_date='-1y', end_date='now')
        user_id = random.choice(user_ids)
        
        # Önce sipariş taslağı
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
        
        # Sipariş kalemleri
        total_amount = 0
        num_items = random.randint(1, 5)
        selected_products = random.sample(product_ids, num_items)
        
        for pid in selected_products:
            # Ürün fiyatını al
            price_row = execute_query("SELECT CurrentPrice FROM Product WHERE ProductID = %s", (pid,))
            price = float(price_row[0]['currentprice'])
            qty = random.randint(1, 3)
            
            execute_query("""
                INSERT INTO OrderItem (OrderID, ProductID, Quantity, UnitPrice)
                VALUES (%s, %s, %s, %s)
            """, (order_id, pid, qty, price), fetch=False)
            
            total_amount += price * qty
            
            # Stok güncelle (Eğer completed ise)
            # Not: Normalde trigger yapar ama şimdilik manuel azaltıyoruz
            execute_query("UPDATE Inventory SET StockQuantity = GREATEST(0, StockQuantity - %s) WHERE ProductID = %s", (qty, pid), fetch=False)
            
        # Toplam tutarı güncelle
        execute_query("UPDATE \"Order\" SET TotalAmount = %s WHERE OrderID = %s", (total_amount, order_id), fetch=False)

if __name__ == "__main__":
    print("[INFO] Otomatik veri uretimi baslatiliyor...")
    clear_database()
    generate_users(50)
    generate_suppliers(10)
    generate_categories()
    generate_products(100)
    generate_orders(200)
    print("[SUCCESS] Tum veriler basariyla olusturuldu!")
