-- ============================================
-- USER TABLE MIGRATIONS
-- Email ve PhoneNumber için UNIQUE constraint
-- ============================================

-- PhoneNumber'a UNIQUE constraint ekle
-- (Email zaten UNIQUE olarak tanımlı)

ALTER TABLE "User" 
ADD CONSTRAINT unique_phone_number UNIQUE (PhoneNumber);

-- NOT: Bu migration'ı çalıştırmadan önce 
-- aynı telefon numarasına sahip kullanıcılar varsa hata verecektir.
-- Önce duplicate'leri temizlemeniz gerekebilir.
