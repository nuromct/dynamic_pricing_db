# 🚀 Dynamic Pricing & Inventory Management System

Bu proje, e-ticaret siteleri için **Dinamik Fiyatlandırma** ve **Envanter Yönetimi** sağlayan kapsamlı bir veritabanı ve web uygulamasıdır.

## 🌟 Özellikler

- **Veritabanı:** PostgreSQL üzerinde 8 ilişkisel tablo (3NF uyumlu).
- **Backend:** Python FastAPI ile geliştirlmiş RESTful API.
- **Frontend:** HTML/CSS/JS ile modern, responsive Dashboard.
- **Otomasyon:** Stok azaldığında fiyatı otomatik artıran **Database Triggers**.
- **Simülasyon:** Gerçek zamanlı trafik ve sipariş simülasyonu.

## 🛠️ Kurulum

### 1. Gereksinimler
- Python 3.8+
- PostgreSQL
- pgAdmin (Opsiyonel, yönetim için)

### 2. Bağımlılıkları Yükle
```bash
pip install -r requirements.txt
```

### 3. Veritabanı Ayarları
`.env` dosyasını kendi PostgreSQL şifrenize göre düzenleyin:
```
DB_PASSWORD=sifreniz
```

## 🚀 Çalıştırma

### Adım 1: Veritabanını Oluştur ve Doldur
Otomatik veri üretici script ile tabloları oluşturun ve dummy verilerle doldurun:
```bash
python generate_data.py
```

### Adım 2: Trigger'ları Yükle (Otomatik Fiyatlandırma için)
```bash
python apply_triggers.py
```

### Adım 3: Sunucuyu Başlat
API ve Web arayüzünü başlatmak için:
```bash
python -m uvicorn main:app --reload
```
Tarayıcıda **http://127.0.0.1:8000** adresine gidin.

### Adım 4: Canlı Simülasyonu Başlat (Opsiyonel)
Sisteme sürekli sipariş gelmesini ve stokların değişmesini izlemek için yeni bir terminalde:
```bash
python simulate_orders.py
```

## 📂 Proje Yapısı

- `main.py`: FastAPI backend uygulaması.
- `database.py`: Veritabanı bağlantı modülü.
- `static/`: Frontend dosyaları (HTML, CSS, JS).
- `generate_data.py`: Dummy veri üretim scripti.
- `simulate_orders.py`: Canlı sipariş botu.
- `04_create_triggers.sql`: Veritabanı trigger tanımları.

## 🤖 Otomatik Fiyatlandırma Mantığı

Sistemde bir **Trigger** bulunur:
- Eğer bir ürünün Stoğu `LowStockThreshold` (10) altına düşerse,
- Ve son 24 saat içinde otomatik zam yapılmamışsa,
- **Fiyat otomatik olarak %10 artırılır.**

## 👥 Katkıda Bulunanlar

- Nurettin (Proje Sahibi)
- Antigravity (AI Assistant)
