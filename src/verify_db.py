import sqlite3
import os

DB_PATH = os.path.join("data", "jade_inventory.db")
SCHEMA_PATH = os.path.join("data", "schema.sql")

def init_and_verify_db():
    # 1. Initialize if not exists (since the shell command failed)
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}. Initializing...")
        conn = sqlite3.connect(DB_PATH)
        with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
            conn.executescript(schema_sql)
        conn.close()
        print("Database initialized.")
    
    # 2. Verify Tables
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    expected_tables = ["items", "images", "item_images", "telemetry"]
    missing = [t for t in expected_tables if t not in tables]
    
    if not missing:
        print("SUCCESS: All tables found:", tables)
        return True
    else:
        print("FAILURE: Missing tables:", missing)
        return False

if __name__ == "__main__":
    init_and_verify_db()
