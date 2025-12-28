INSERT INTO "User" (FullName, Email, PasswordHash, Role, PhoneNumber) VALUES
('Nurettin Macit', 'macit@gmail.com', 'hashed_password_1', 'seller', '5551234567'),
('Muhammed Özdemir', 'admin@admin.com', 'hashed_password_2', 'admin', '5051234567'),
('Bilal Cebeci', 'bilal@gmail.com', 'hashed_password_3', 'customer', '5311234567');

INSERT INTO Category (CategoryName, Description) VALUES
('Electronics', 'Phones, computers and electronic devices'),
('Clothing', 'Clothing and accessories'),
('Sports', 'Sports equipment and gear');

INSERT INTO Supplier (CompanyName, ContactEmail, TaxNumber, Address) VALUES
('Cebeci Inc.', 'info@cebeci.com', '123456789', 'Istanbul, Turkey'),
('Macit Clothing', 'sales@macit.com', '987654321', 'Ankara, Turkey');

INSERT INTO Product (Title, Description, BasePrice, CurrentPrice, IsActive, CategoryID, SupplierID) VALUES
('iPhone 15', 'Apple iPhone 15 128GB', 45000.00, 47500.00, TRUE, 1, 1),
('Bosch Refrigerator', 'Bosch NoFrost Refrigerator', 70000.00, 70000.00, TRUE, 1, 1),
('Adidas T-shirt', 'Adidas Originals Men''s T-shirt', 1200.00, 1100.00, TRUE, 2, 2),
('Soccer Ball', 'Nike Premier League Soccer Ball', 800.00, 900.00, TRUE, 3, NULL);

INSERT INTO Inventory (ProductID, StockQuantity, LowStockThreshold, HighStockThreshold) VALUES
(1, 5, 10, 100),   
(2, 45, 10, 100),  
(3, 120, 20, 200), 
(4, 8, 15, 80);    

INSERT INTO PriceHistory (ProductID, OldPrice, NewPrice, ChangeDate, Reason) VALUES
(1, 45000.00, 47500.00, '2025-12-08', 'low_stock'),      
(3, 1200.00, 1100.00, '2025-12-09', 'campaign'),         
(4, 800.00, 900.00, '2025-12-11', 'low_stock');          

INSERT INTO "Order" (UserID, OrderDate, Status, TotalAmount, ShippingAddress) VALUES
(3, '2025-12-10', 'completed', 47500.00, 'Maslak, Istanbul'),
(3, '2025-12-11', 'pending', 2700.00, 'Maslak, Istanbul');

INSERT INTO OrderItem (OrderID, ProductID, Quantity, UnitPrice) VALUES
(1, 1, 1, 47500.00),  
(2, 3, 3, 1100.00),   
(2, 4, 2, 800.00);    
