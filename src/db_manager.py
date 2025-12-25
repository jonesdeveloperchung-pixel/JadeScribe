import sqlite3
import json
import logging
import os
import csv
import io
from typing import Dict, Any, Optional, List
from datetime import datetime

# Configure Logging
logger = logging.getLogger(__name__)

DB_PATH = os.path.join("data", "jade_inventory.db")

def reset_database():
    """
    WARNING: Drops all tables and re-initializes the database from schema.sql.
    This action is irreversible.
    """
    try:
        # 1. Close any existing connections (best effort)
        # In this simple app, we open/close per request, so it should be fine.
        
        # 2. Re-run Schema
        SCHEMA_PATH = os.path.join("data", "schema.sql")
        if not os.path.exists(SCHEMA_PATH):
            logger.error(f"Schema file not found at {SCHEMA_PATH}")
            return False

        if os.path.exists(DB_PATH):
            os.remove(DB_PATH) # Delete the file completely to ensure clean slate
            logger.info("Existing database file deleted.")

        conn = sqlite3.connect(DB_PATH)
        with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        conn.close()
        
        logger.info("Database has been reset successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to reset database: {e}")
        return False

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row # Access columns by name
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection failed: {e}")
        return None

def check_and_migrate_db():
    """Checks for schema updates and applies them if necessary."""
    conn = get_db_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        
        # Check existing columns in 'items' table
        cursor.execute("PRAGMA table_info(items)")
        columns = [row['name'] for row in cursor.fetchall()]
        
        # Add 'description_modern' if missing
        if 'description_modern' not in columns:
            logger.info("Migrating DB: Adding 'description_modern' column.")
            cursor.execute("ALTER TABLE items ADD COLUMN description_modern TEXT")
            
        # Add 'description_social' if missing
        if 'description_social' not in columns:
            logger.info("Migrating DB: Adding 'description_social' column.")
            cursor.execute("ALTER TABLE items ADD COLUMN description_social TEXT")
            
        # Add 'rarity_rank' if missing (New in v1.2)
        if 'rarity_rank' not in columns:
            logger.info("Migrating DB: Adding 'rarity_rank' column.")
            cursor.execute("ALTER TABLE items ADD COLUMN rarity_rank TEXT DEFAULT 'B'")
            
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Database migration failed: {e}")
    finally:
        conn.close()

def log_telemetry(
    module: str,
    action: str,
    execution_data: Dict[str, Any] = None,
    context: Dict[str, Any] = None,
    args: List[str] = None
):
    """
    Logs an event to the telemetry table.
    """
    conn = get_db_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        
        # Defaults
        execution_data = execution_data or {}
        context = context or {}
        args = args or []
        
        query = """
            INSERT INTO telemetry (
                program, version, module, action, args, 
                duration_ms, cpu_time_ms, gpu_time_ms, memory_mb, 
                exit_code, error, context_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        values = (
            "jade-scribe", "1.0.0", module, action, json.dumps(args),
            execution_data.get("duration_ms", 0),
            execution_data.get("cpu_time_ms", 0),
            execution_data.get("gpu_time_ms", 0),
            execution_data.get("memory_mb", 0),
            execution_data.get("exit_code", 0),
            execution_data.get("error", None),
            json.dumps(context)
        )
        
        cursor.execute(query, values)
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Failed to log telemetry: {e}")
    finally:
        conn.close()

def save_item(item_data: Dict[str, Any]):
    """
    Saves or updates a jade item in the database.
    
    Args:
        item_data: Dictionary containing 'item_code', 'title', 'description_hero', 
                   'description_modern', 'description_social', 'attributes', 'rarity_rank'.
    """
    conn = get_db_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        
        query = """
            INSERT INTO items (
                item_code, title, description_hero, description_modern, description_social, 
                attributes_json, rarity_rank, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(item_code) DO UPDATE SET
                title=excluded.title,
                description_hero=excluded.description_hero,
                description_modern=excluded.description_modern,
                description_social=excluded.description_social,
                attributes_json=excluded.attributes_json,
                rarity_rank=excluded.rarity_rank,
                updated_at=CURRENT_TIMESTAMP
        """
        
        values = (
            item_data["item_code"],
            item_data.get("title", ""),
            item_data.get("description_hero", ""),
            item_data.get("description_modern", ""),
            item_data.get("description_social", ""),
            json.dumps(item_data.get("attributes", {})),
            item_data.get("rarity_rank", "B")
        )
        
        cursor.execute(query, values)
        conn.commit()
        logger.info(f"Item saved successfully: {item_data['item_code']}")
        return True
        
    except sqlite3.Error as e:
        logger.error(f"Failed to save item {item_data.get('item_code')}: {e}")
        return False
    finally:
        conn.close()

def get_all_items() -> List[Dict[str, Any]]:
    """Retrieves all items from the database."""
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items ORDER BY updated_at DESC")
        rows = cursor.fetchall()
        
        items = []
        for row in rows:
            items.append(dict(row))
        return items
        
    except sqlite3.Error as e:
        logger.error(f"Failed to retrieve items: {e}")
        return []
    finally:
        conn.close()

def export_items_to_csv() -> str:
    """Exports all items to a CSV string."""
    items = get_all_items()
    if not items:
        return ""
    
    output = io.StringIO()
    # Define headers
    headers = [
        "item_code", "title", "rarity_rank",
        "description_hero", "description_modern", "description_social",
        "attributes_json", "updated_at"
    ]
    
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    
    for item in items:
        # Filter item dict to match headers
        row = {k: item[k] for k in headers if k in item}
        writer.writerow(row)
        
    return output.getvalue()

