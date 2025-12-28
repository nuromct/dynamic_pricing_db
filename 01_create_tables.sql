-- ============================================
-- DYNAMIC PRICING AND INVENTORY MANAGEMENT SYSTEM
-- PostgreSQL Database Schema
-- ============================================

-- 1. USER TABLOSU
-- Sistemdeki tüm kullanıcılar (müşteri, satıcı, admin)
CREATE TABLE "User" (
    UserID SERIAL PRIMARY KEY,
    FullName VARCHAR(100) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    PasswordHash VARCHAR(255) NOT NULL,
    Role VARCHAR(20) NOT NULL CHECK (Role IN ('customer', 'seller', 'admin')),
    PhoneNumber VARCHAR(20),
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. CATEGORY TABLOSU
-- Ürün kategorileri
CREATE TABLE Category (
    CategoryID SERIAL PRIMARY KEY,
    CategoryName VARCHAR(100) NOT NULL,
    Description TEXT
);

-- 3. SUPPLIER TABLOSU
-- Tedarikçi şirketler
CREATE TABLE Supplier (
    SupplierID SERIAL PRIMARY KEY,
    CompanyName VARCHAR(100) NOT NULL,
    ContactEmail VARCHAR(100),
    TaxNumber VARCHAR(20),
    Address TEXT
);

-- 4. PRODUCT TABLOSU
-- Satılan ürünler
CREATE TABLE Product (
    ProductID SERIAL PRIMARY KEY,
    Title VARCHAR(200) NOT NULL,
    Description TEXT,
    BasePrice DECIMAL(10, 2) NOT NULL,
    CurrentPrice DECIMAL(10, 2) NOT NULL,
    IsActive BOOLEAN DEFAULT TRUE,
    CategoryID INTEGER REFERENCES Category(CategoryID),
    SupplierID INTEGER REFERENCES Supplier(SupplierID)
);

-- 5. INVENTORY TABLOSU
-- Her ürünün stok bilgisi
CREATE TABLE Inventory (
    InventoryID SERIAL PRIMARY KEY,
    ProductID INTEGER UNIQUE REFERENCES Product(ProductID),
    StockQuantity INTEGER NOT NULL DEFAULT 0,
    LowStockThreshold INTEGER DEFAULT 10,
    HighStockThreshold INTEGER DEFAULT 100,
    LastRestockDate DATE
);

-- 6. PRICEHISTORY TABLOSU
-- Fiyat değişikliği geçmişi (dinamik fiyatlandırma için)
CREATE TABLE PriceHistory (
    HistoryID SERIAL PRIMARY KEY,
    ProductID INTEGER REFERENCES Product(ProductID),
    OldPrice DECIMAL(10, 2) NOT NULL,
    NewPrice DECIMAL(10, 2) NOT NULL,
    ChangeDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Reason VARCHAR(50) -- 'low_stock', 'campaign', 'demand_increase' vb.
);

-- 7. ORDER TABLOSU
-- Siparişler
CREATE TABLE "Order" (
    OrderID SERIAL PRIMARY KEY,
    UserID INTEGER REFERENCES "User"(UserID),
    OrderDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Status VARCHAR(20) DEFAULT 'pending' CHECK (Status IN ('pending', 'processing', 'completed', 'cancelled')),
    TotalAmount DECIMAL(10, 2) NOT NULL,
    ShippingAddress TEXT NOT NULL
);

-- 8. ORDERITEM TABLOSU
-- Siparişteki her ürün detayı (Many-to-Many ilişkisi için)
CREATE TABLE OrderItem (
    ItemID SERIAL PRIMARY KEY,
    OrderID INTEGER REFERENCES "Order"(OrderID),
    ProductID INTEGER REFERENCES Product(ProductID),
    Quantity INTEGER NOT NULL CHECK (Quantity > 0),
    UnitPrice DECIMAL(10, 2) NOT NULL
);

-- ============================================
-- INDEXLER (Performans için)
-- ============================================
CREATE INDEX idx_product_category ON Product(CategoryID);
CREATE INDEX idx_product_supplier ON Product(SupplierID);
CREATE INDEX idx_order_user ON "Order"(UserID);
CREATE INDEX idx_orderitem_order ON OrderItem(OrderID);
CREATE INDEX idx_pricehistory_product ON PriceHistory(ProductID);
