"""
Database Connection Module
PostgreSQL veritabanına bağlantı yönetimi
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# .env dosyasından değişkenleri yükle
load_dotenv()

def get_db_connection():
    """Veritabanı bağlantısı oluştur"""
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "dynamic_pricing_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        cursor_factory=RealDictCursor
    )
    return conn

def execute_query(query: str, params: tuple = None, fetch: bool = True):
    """SQL sorgusu çalıştır"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        if fetch:
            result = cursor.fetchall()
            conn.commit()  # <--- Ekleme: Veri döndüren işlem olsa bile commit et (INSERT RETURNING için)
        else:
            conn.commit()
            result = cursor.rowcount
        return result
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()
