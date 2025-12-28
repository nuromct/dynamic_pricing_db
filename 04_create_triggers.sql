CREATE OR REPLACE FUNCTION check_low_stock_pricing()
RETURNS TRIGGER AS $$
DECLARE
    current_price DECIMAL(10, 2);
    min_threshold INTEGER;
BEGIN
    IF NEW.StockQuantity < OLD.StockQuantity AND NEW.StockQuantity <= NEW.LowStockThreshold THEN
        
        SELECT CurrentPrice INTO current_price FROM Product WHERE ProductID = NEW.ProductID;
        
        IF NOT EXISTS (
            SELECT 1 FROM PriceHistory 
            WHERE ProductID = NEW.ProductID 
            AND Reason = 'low_stock' 
            AND ChangeDate > NOW() - INTERVAL '1 day'
        ) THEN
            UPDATE Product SET CurrentPrice = current_price * 1.10 WHERE ProductID = NEW.ProductID;
            
            INSERT INTO PriceHistory (ProductID, OldPrice, NewPrice, Reason, ChangeDate)
            VALUES (NEW.ProductID, current_price, current_price * 1.10, 'low_stock', NOW());
            
            RAISE NOTICE 'Product % price INCREASED due to low stock.', NEW.ProductID;
        END IF;

    ELSIF NEW.StockQuantity > OLD.StockQuantity AND NEW.StockQuantity >= NEW.HighStockThreshold THEN
        
        SELECT CurrentPrice INTO current_price FROM Product WHERE ProductID = NEW.ProductID;
        
        IF NOT EXISTS (
            SELECT 1 FROM PriceHistory 
            WHERE ProductID = NEW.ProductID 
            AND Reason = 'high_stock' 
            AND ChangeDate > NOW() - INTERVAL '1 day'
        ) THEN
            UPDATE Product SET CurrentPrice = current_price * 0.90 WHERE ProductID = NEW.ProductID;
            
            INSERT INTO PriceHistory (ProductID, OldPrice, NewPrice, Reason, ChangeDate)
            VALUES (NEW.ProductID, current_price, current_price * 0.90, 'high_stock', NOW());
            
            RAISE NOTICE 'Product % price DECREASED due to high stock.', NEW.ProductID;
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_low_stock_pricing ON Inventory;

CREATE TRIGGER trg_low_stock_pricing
AFTER UPDATE OF StockQuantity
ON Inventory
FOR EACH ROW
EXECUTE FUNCTION check_low_stock_pricing();

CREATE OR REPLACE FUNCTION log_price_change()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.CurrentPrice <> OLD.CurrentPrice THEN
        NULL; 
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
