import sqlite3
import json
import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime

# Configure Logging
logger = logging.getLogger(__name__)

DB_PATH = os.path.join("data", "jade_inventory.db")

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row # Access columns by name
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection failed: {e}")
        return None

def log_telemetry(
    module: str,
    action: str,
    execution_data: Dict[str, Any] = None,
    context: Dict[str, Any] = None,
    args: List[str] = None
):
    """
    Logs an event to the telemetry table.
    
    Args:
        module: The system module (e.g., 'ai_engine', 'ui').
        action: The specific action performed (e.g., 'scan_image').
        execution_data: Metrics like duration_ms, memory_mb, etc.
        context: Contextual info like tags or environment.
        args: Function arguments or inputs.
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
        item_data: Dictionary containing 'item_code', 'title', 'description_hero', 'attributes'.
    """
    conn = get_db_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        
        query = """
            INSERT INTO items (item_code, title, description_hero, attributes_json, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(item_code) DO UPDATE SET
                title=excluded.title,
                description_hero=excluded.description_hero,
                attributes_json=excluded.attributes_json,
                updated_at=CURRENT_TIMESTAMP
        """
        
        values = (
            item_data["item_code"],
            item_data.get("title", ""),
            item_data.get("description_hero", ""),
            json.dumps(item_data.get("attributes", {}))
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
