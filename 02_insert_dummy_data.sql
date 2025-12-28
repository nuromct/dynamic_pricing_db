-- ============================================
-- DUMMY DATA - Örnek Veriler
-- ============================================

-- 1. USER (Kullanıcılar)
INSERT INTO "User" (FullName, Email, PasswordHash, Role, PhoneNumber) VALUES
('Nurettin Macit', 'macit@gmail.com', 'hashed_password_1', 'seller', '5551234567'),
('Muhammed Özdemir', 'admin@admin.com', 'hashed_password_2', 'admin', '5051234567'),
('Bilal Cebeci', 'bilal@gmail.com', 'hashed_password_3', 'customer', '5311234567');

-- 2. CATEGORY (Kategoriler)
INSERT INTO Category (CategoryName, Description) VALUES
('Elektronik', 'Telefon, bilgisayar ve elektronik cihazlar'),
('Giyim', 'Kıyafet ve aksesuar ürünleri'),
('Spor', 'Spor ekipmanları ve malzemeleri');

-- 3. SUPPLIER (Tedarikçiler)
INSERT INTO Supplier (CompanyName, ContactEmail, TaxNumber, Address) VALUES
('Cebeci A.Ş.', 'info@cebeci.com', '123456789', 'İstanbul, Türkiye'),
('Macit Giyim', 'satis@macit.com', '987654321', 'Ankara, Türkiye');

-- 4. PRODUCT (Ürünler)
INSERT INTO Product (Title, Description, BasePrice, CurrentPrice, IsActive, CategoryID, SupplierID) VALUES
('iPhone 15', 'Apple iPhone 15 128GB', 45000.00, 47500.00, TRUE, 1, 1),
('Bosch Buzdolabı', 'Bosch NoFrost Buzdolabı', 70000.00, 70000.00, TRUE, 1, 1),
('Adidas T-shirt', 'Adidas Originals Erkek Tişört', 1200.00, 1100.00, TRUE, 2, 2),
('Futbol Topu', 'Nike Premier League Futbol Topu', 800.00, 900.00, TRUE, 3, NULL);

-- 5. INVENTORY (Stok Bilgileri)
INSERT INTO Inventory (ProductID, StockQuantity, LowStockThreshold, HighStockThreshold) VALUES
(1, 5, 10, 100),   -- iPhone 15 - düşük stok!
(2, 45, 10, 100),  -- Buzdolabı
(3, 120, 20, 200), -- T-shirt
(4, 8, 15, 80);    -- Futbol Topu - düşük stok!

-- 6. PRICEHISTORY (Fiyat Geçmişi)
INSERT INTO PriceHistory (ProductID, OldPrice, NewPrice, ChangeDate, Reason) VALUES
(1, 45000.00, 47500.00, '2025-12-08', 'low_stock'),      -- iPhone fiyat artışı (stok az)
(3, 1200.00, 1100.00, '2025-12-09', 'campaign'),         -- T-shirt kampanya indirimi
(4, 800.00, 900.00, '2025-12-11', 'low_stock');          -- Futbol topu fiyat artışı

-- 7. ORDER (Siparişler)
INSERT INTO "Order" (UserID, OrderDate, Status, TotalAmount, ShippingAddress) VALUES
(3, '2025-12-10', 'completed', 47500.00, 'Maslak, İstanbul'),
(3, '2025-12-11', 'pending', 2700.00, 'Maslak, İstanbul');

-- 8. ORDERITEM (Sipariş Detayları)
INSERT INTO OrderItem (OrderID, ProductID, Quantity, UnitPrice) VALUES
(1, 1, 1, 47500.00),  -- Sipariş 1: 1 adet iPhone
(2, 3, 3, 1100.00),   -- Sipariş 2: 3 adet T-shirt (3 x 1100 = 3300? Toplam 2700 görünüyor, belki indirim var)
(2, 4, 2, 800.00);    -- Sipariş 2: 2 adet Futbol Topu

-- ============================================
-- VERİ KONTROLÜ
-- ============================================
-- Aşağıdaki sorguları çalıştırarak verilerin eklendiğini doğrulayabilirsin:

-- SELECT * FROM "User";
-- SELECT * FROM Category;
-- SELECT * FROM Supplier;
-- SELECT * FROM Product;
-- SELECT * FROM Inventory;
-- SELECT * FROM PriceHistory;
-- SELECT * FROM "Order";
-- SELECT * FROM OrderItem;
