from database import execute_query, get_db_connection

def apply_triggers():
    print("[INFO] Trigger'lar yukleniyor...")
    try:
        with open("04_create_triggers.sql", "r", encoding="utf-8") as f:
            sql_content = f.read()
            
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(sql_content)
        conn.commit()
        conn.close()
        print("[SUCCESS] Trigger'lar basariyla olusturuldu!")
    except Exception as e:
        print(f"[ERROR] Hata: {e}")

if __name__ == "__main__":
    apply_triggers()
