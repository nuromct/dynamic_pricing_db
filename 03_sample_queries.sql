-- ============================================
-- ÖRNEK SORGULAR (QUERIES)
-- ============================================

-- ----------------------------------------
-- 1. TEMEL SELECT SORGULARI
-- ----------------------------------------

-- Tüm ürünleri listele
SELECT * FROM Product;

-- Sadece aktif ürünleri listele
SELECT ProductID, Title, CurrentPrice 
FROM Product 
WHERE IsActive = TRUE;

-- Fiyatı 1000 TL'den fazla olan ürünler
SELECT Title, CurrentPrice 
FROM Product 
WHERE CurrentPrice > 1000
ORDER BY CurrentPrice DESC;

-- ----------------------------------------
-- 2. JOIN SORGULARI (Tabloları Birleştirme)
-- ----------------------------------------

-- Ürünleri kategorileriyle birlikte göster
SELECT 
    p.Title AS "Ürün Adı",
    p.CurrentPrice AS "Fiyat",
    c.CategoryName AS "Kategori"
FROM Product p
INNER JOIN Category c ON p.CategoryID = c.CategoryID;

-- Ürünleri tedarikçileriyle birlikte göster
SELECT 
    p.Title AS "Ürün",
    s.CompanyName AS "Tedarikçi",
    p.CurrentPrice AS "Fiyat"
FROM Product p
LEFT JOIN Supplier s ON p.SupplierID = s.SupplierID;

-- Kullanıcı siparişlerini göster
SELECT 
    u.FullName AS "Müşteri",
    o.OrderID AS "Sipariş No",
    o.OrderDate AS "Tarih",
    o.TotalAmount AS "Toplam",
    o.Status AS "Durum"
FROM "Order" o
INNER JOIN "User" u ON o.UserID = u.UserID;

-- ----------------------------------------
-- 3. STOK SORGULARI (Envanter Yönetimi)
-- ----------------------------------------

-- Düşük stoklu ürünleri bul (stok < eşik değeri)
SELECT 
    p.Title AS "Ürün",
    i.StockQuantity AS "Mevcut Stok",
    i.LowStockThreshold AS "Minimum Stok"
FROM Inventory i
INNER JOIN Product p ON i.ProductID = p.ProductID
WHERE i.StockQuantity < i.LowStockThreshold;

-- Stok durumu özeti
SELECT 
    p.Title,
    i.StockQuantity,
    CASE 
        WHEN i.StockQuantity < i.LowStockThreshold THEN 'DÜŞÜK STOK!'
        WHEN i.StockQuantity > i.HighStockThreshold THEN 'FAZLA STOK'
        ELSE 'NORMAL'
    END AS "Stok Durumu"
FROM Inventory i
INNER JOIN Product p ON i.ProductID = p.ProductID;

-- ----------------------------------------
-- 4. FİYAT ANALİZİ (Dinamik Fiyatlandırma)
-- ----------------------------------------

-- Fiyat değişiklik geçmişi
SELECT 
    p.Title AS "Ürün",
    ph.OldPrice AS "Eski Fiyat",
    ph.NewPrice AS "Yeni Fiyat",
    (ph.NewPrice - ph.OldPrice) AS "Fark",
    ph.Reason AS "Sebep",
    ph.ChangeDate AS "Tarih"
FROM PriceHistory ph
INNER JOIN Product p ON ph.ProductID = p.ProductID
ORDER BY ph.ChangeDate DESC;

-- Düşük stok nedeniyle fiyat artan ürünler
SELECT 
    p.Title,
    ph.OldPrice,
    ph.NewPrice,
    ROUND(((ph.NewPrice - ph.OldPrice) / ph.OldPrice * 100), 2) AS "Artış %"
FROM PriceHistory ph
INNER JOIN Product p ON ph.ProductID = p.ProductID
WHERE ph.Reason = 'low_stock';

-- ----------------------------------------
-- 5. SİPARİŞ ANALİZİ
-- ----------------------------------------

-- Sipariş detayları (hangi üründen kaç tane alındı)
SELECT 
    o.OrderID AS "Sipariş No",
    u.FullName AS "Müşteri",
    p.Title AS "Ürün",
    oi.Quantity AS "Adet",
    oi.UnitPrice AS "Birim Fiyat",
    (oi.Quantity * oi.UnitPrice) AS "Ara Toplam"
FROM OrderItem oi
INNER JOIN "Order" o ON oi.OrderID = o.OrderID
INNER JOIN "User" u ON o.UserID = u.UserID
INNER JOIN Product p ON oi.ProductID = p.ProductID;

-- ----------------------------------------
-- 6. AGGREGATE FONKSİYONLAR (Özet İstatistikler)
-- ----------------------------------------

-- Toplam ürün sayısı
SELECT COUNT(*) AS "Toplam Ürün" FROM Product;

-- Ortalama ürün fiyatı
SELECT ROUND(AVG(CurrentPrice), 2) AS "Ortalama Fiyat" FROM Product;

-- Kategori bazında ürün sayısı
SELECT 
    c.CategoryName AS "Kategori",
    COUNT(p.ProductID) AS "Ürün Sayısı",
    ROUND(AVG(p.CurrentPrice), 2) AS "Ort. Fiyat"
FROM Category c
LEFT JOIN Product p ON c.CategoryID = p.CategoryID
GROUP BY c.CategoryID, c.CategoryName;

-- Toplam stok değeri
SELECT 
    SUM(p.CurrentPrice * i.StockQuantity) AS "Toplam Stok Değeri"
FROM Product p
INNER JOIN Inventory i ON p.ProductID = i.ProductID;

-- ----------------------------------------
-- 7. EN ÇOK / EN AZ SORGULARI
-- ----------------------------------------

-- En pahalı 3 ürün
SELECT Title, CurrentPrice 
FROM Product 
ORDER BY CurrentPrice DESC 
LIMIT 3;

-- En düşük stoklu ürün
SELECT 
    p.Title, 
    i.StockQuantity
FROM Inventory i
INNER JOIN Product p ON i.ProductID = p.ProductID
ORDER BY i.StockQuantity ASC
LIMIT 1;

-- En çok sipariş veren müşteri
SELECT 
    u.FullName,
    COUNT(o.OrderID) AS "Sipariş Sayısı",
    SUM(o.TotalAmount) AS "Toplam Harcama"
FROM "User" u
INNER JOIN "Order" o ON u.UserID = o.UserID
GROUP BY u.UserID, u.FullName
ORDER BY "Toplam Harcama" DESC
LIMIT 1;
