from database import execute_query, get_db_connection

def apply_triggers():
    print("[INFO] Loading triggers...")
    try:
        with open("04_create_triggers.sql", "r", encoding="utf-8") as f:
            sql_content = f.read()
            
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(sql_content)
        conn.commit()
        conn.close()
        print("[SUCCESS] Triggers successfully created!")
    except Exception as e:
        print(f"[ERROR] Error: {e}")

if __name__ == "__main__":
    apply_triggers()
