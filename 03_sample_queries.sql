SELECT * FROM Product;

SELECT ProductID, Title, CurrentPrice 
FROM Product 
WHERE IsActive = TRUE;

SELECT Title, CurrentPrice 
FROM Product 
WHERE CurrentPrice > 1000
ORDER BY CurrentPrice DESC;

SELECT 
    p.Title AS "Product Name",
    p.CurrentPrice AS "Price",
    c.CategoryName AS "Category"
FROM Product p
INNER JOIN Category c ON p.CategoryID = c.CategoryID;

SELECT 
    p.Title AS "Product",
    s.CompanyName AS "Supplier",
    p.CurrentPrice AS "Price"
FROM Product p
LEFT JOIN Supplier s ON p.SupplierID = s.SupplierID;

SELECT 
    u.FullName AS "Customer",
    o.OrderID AS "Order No",
    o.OrderDate AS "Date",
    o.TotalAmount AS "Total",
    o.Status AS "Status"
FROM "Order" o
INNER JOIN "User" u ON o.UserID = u.UserID;

SELECT 
    p.Title AS "Product",
    i.StockQuantity AS "Current Stock",
    i.LowStockThreshold AS "Minimum Stock"
FROM Inventory i
INNER JOIN Product p ON i.ProductID = p.ProductID
WHERE i.StockQuantity < i.LowStockThreshold;

SELECT 
    p.Title,
    i.StockQuantity,
    CASE 
        WHEN i.StockQuantity < i.LowStockThreshold THEN 'LOW STOCK!'
        WHEN i.StockQuantity > i.HighStockThreshold THEN 'OVER STOCK'
        ELSE 'NORMAL'
    END AS "Stock Status"
FROM Inventory i
INNER JOIN Product p ON i.ProductID = p.ProductID;

SELECT 
    p.Title AS "Product",
    ph.OldPrice AS "Old Price",
    ph.NewPrice AS "New Price",
    (ph.NewPrice - ph.OldPrice) AS "Difference",
    ph.Reason AS "Reason",
    ph.ChangeDate AS "Date"
FROM PriceHistory ph
INNER JOIN Product p ON ph.ProductID = p.ProductID
ORDER BY ph.ChangeDate DESC;

SELECT 
    p.Title,
    ph.OldPrice,
    ph.NewPrice,
    ROUND(((ph.NewPrice - ph.OldPrice) / ph.OldPrice * 100), 2) AS "Increase %"
FROM PriceHistory ph
INNER JOIN Product p ON ph.ProductID = p.ProductID
WHERE ph.Reason = 'low_stock';

SELECT 
    o.OrderID AS "Order No",
    u.FullName AS "Customer",
    p.Title AS "Product",
    oi.Quantity AS "Qty",
    oi.UnitPrice AS "Unit Price",
    (oi.Quantity * oi.UnitPrice) AS "Subtotal"
FROM OrderItem oi
INNER JOIN "Order" o ON oi.OrderID = o.OrderID
INNER JOIN "User" u ON o.UserID = u.UserID
INNER JOIN Product p ON oi.ProductID = p.ProductID;

SELECT COUNT(*) AS "Total Products" FROM Product;

SELECT ROUND(AVG(CurrentPrice), 2) AS "Average Price" FROM Product;

SELECT 
    c.CategoryName AS "Category",
    COUNT(p.ProductID) AS "Product Count",
    ROUND(AVG(p.CurrentPrice), 2) AS "Avg. Price"
FROM Category c
LEFT JOIN Product p ON c.CategoryID = p.CategoryID
GROUP BY c.CategoryID, c.CategoryName;

SELECT 
    SUM(p.CurrentPrice * i.StockQuantity) AS "Total Stock Value"
FROM Product p
INNER JOIN Inventory i ON p.ProductID = i.ProductID;

SELECT Title, CurrentPrice 
FROM Product 
ORDER BY CurrentPrice DESC 
LIMIT 3;

SELECT 
    p.Title, 
    i.StockQuantity
FROM Inventory i
INNER JOIN Product p ON i.ProductID = p.ProductID
ORDER BY i.StockQuantity ASC
LIMIT 1;

SELECT 
    u.FullName,
    COUNT(o.OrderID) AS "Order Count",
    SUM(o.TotalAmount) AS "Total Spending"
FROM "User" u
INNER JOIN "Order" o ON u.UserID = o.UserID
GROUP BY u.UserID, u.FullName
ORDER BY "Total Spending" DESC
LIMIT 1;
