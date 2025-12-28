-- ============================================
-- DYNAMIC PRICING TRIGGERS
-- Otomatik Fiyatlandırma Mekanizması
-- ============================================

-- 1. STOK AZALDIĞINDA FİYAT ARTIRMA TRIGGER FONKSİYONU
CREATE OR REPLACE FUNCTION check_low_stock_pricing()
RETURNS TRIGGER AS $$
DECLARE
    current_price DECIMAL(10, 2);
    min_threshold INTEGER;
BEGIN
    -- 1. DÜŞÜK STOK (ZAM)
    IF NEW.StockQuantity < OLD.StockQuantity AND NEW.StockQuantity <= NEW.LowStockThreshold THEN
        
        -- Güncel fiyatı al
        SELECT CurrentPrice INTO current_price FROM Product WHERE ProductID = NEW.ProductID;
        
        -- Son 24 saatte zaten zam yapılmamışsa
        IF NOT EXISTS (
            SELECT 1 FROM PriceHistory 
            WHERE ProductID = NEW.ProductID 
            AND Reason = 'low_stock' 
            AND ChangeDate > NOW() - INTERVAL '1 day'
        ) THEN
            UPDATE Product SET CurrentPrice = current_price * 1.10 WHERE ProductID = NEW.ProductID;
            
            INSERT INTO PriceHistory (ProductID, OldPrice, NewPrice, Reason, ChangeDate)
            VALUES (NEW.ProductID, current_price, current_price * 1.10, 'low_stock', NOW());
            
            RAISE NOTICE 'Düşük stok nedeniyle ürün % fiyatı ARTIRILDI.', NEW.ProductID;
        END IF;

    -- 2. YÜKSEK STOK (İNDİRİM)
    ELSIF NEW.StockQuantity > OLD.StockQuantity AND NEW.StockQuantity >= NEW.HighStockThreshold THEN
        
        SELECT CurrentPrice INTO current_price FROM Product WHERE ProductID = NEW.ProductID;
        
        -- Son 24 saatte zaten indirim yapılmamışsa
        IF NOT EXISTS (
            SELECT 1 FROM PriceHistory 
            WHERE ProductID = NEW.ProductID 
            AND Reason = 'high_stock' 
            AND ChangeDate > NOW() - INTERVAL '1 day'
        ) THEN
            UPDATE Product SET CurrentPrice = current_price * 0.90 WHERE ProductID = NEW.ProductID;
            
            INSERT INTO PriceHistory (ProductID, OldPrice, NewPrice, Reason, ChangeDate)
            VALUES (NEW.ProductID, current_price, current_price * 0.90, 'high_stock', NOW());
            
            RAISE NOTICE 'Yüksek stok nedeniyle ürün % fiyatı DÜŞÜRÜLDÜ.', NEW.ProductID;
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 2. TRIGGER TANIMLAMA
DROP TRIGGER IF EXISTS trg_low_stock_pricing ON Inventory;

CREATE TRIGGER trg_low_stock_pricing
AFTER UPDATE OF StockQuantity
ON Inventory
FOR EACH ROW
EXECUTE FUNCTION check_low_stock_pricing();

-- 3. FİYAT DEĞİŞİKLİĞİ GEÇMİŞİNİ OTOMATİK KAYDETME (Manuel update'ler için)
CREATE OR REPLACE FUNCTION log_price_change()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.CurrentPrice <> OLD.CurrentPrice THEN
        -- Eğer bu değişiklik trigger tarafından yapılmadıysa (PriceHistory'ye çift kayıt atmamak için kontrol edilebilir ama şimdilik logluyoruz)
        -- Not: Yukarıdaki trigger zaten PriceHistory'ye ekliyor.
        -- Burası sadece manuel veya başka sebeplerle yapılan değişiklikleri yakalar.
        
        -- Basitlik için: Sadece manuel güncellemelerde çalışacak şekilde ayarlayalım
        -- veya yukarıdaki trigger içindeki INSERT'ü kaldırıp buraya bırakabiliriz.
        -- Şimdilik çakışmayı önlemek için burayı pasif bırakıyorum veya sadece 'manual' diye varsayıyorum.
        NULL; 
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
