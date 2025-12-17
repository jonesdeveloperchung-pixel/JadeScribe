import unittest
import os
import json
import sqlite3
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from db_manager import save_item, get_all_items, log_telemetry
from ai_engine import _get_symbolism_context

class TestJadeSystem(unittest.TestCase):

    def setUp(self):
        # Use a temporary database for testing
        self.test_db_path = "data/test_jade.db"
        # Patch db_manager to use test DB (simple monkeypatch approach for this scale)
        import db_manager
        db_manager.DB_PATH = self.test_db_path
        
        # Initialize Schema
        conn = sqlite3.connect(self.test_db_path)
        with open("data/schema.sql", 'r') as f:
            conn.executescript(f.read())
        conn.close()

    def tearDown(self):
        # Clean up test DB
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_database_crud(self):
        """Test saving and retrieving items."""
        item_data = {
            "item_code": "TEST-001",
            "title": "Test Pendant",
            "description_hero": "A beautiful test jade.",
            "attributes": {"color": "green", "motif": "bamboo"}
        }
        
        # Save
        result = save_item(item_data)
        self.assertTrue(result)
        
        # Retrieve
        items = get_all_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['item_code'], "TEST-001")
        
        # Update (Idempotency)
        item_data["title"] = "Updated Title"
        save_item(item_data)
        items = get_all_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['title'], "Updated Title")

    def test_telemetry_logging(self):
        """Test that telemetry is written to DB."""
        log_telemetry(
            module="test_suite",
            action="run_test",
            execution_data={"duration_ms": 100}
        )
        
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM telemetry WHERE module='test_suite'")
        row = cursor.fetchone()
        conn.close()
        
        self.assertIsNotNone(row)
        self.assertEqual(row[6], "run_test") # action column

    def test_symbolism_logic(self):
        """Test that cultural context is retrieved correctly."""
        # Test exact match
        context = _get_symbolism_context("bamboo", "moss_green")
        self.assertIn("竹", context)
        self.assertIn("節節高升", context)
        self.assertIn("油青", context)
        
        # Test case insensitivity
        context = _get_symbolism_context("Bamboo", "MOSS_GREEN")
        self.assertIn("竹", context)
        
        # Test unknown
        context = _get_symbolism_context("UnknownThing", "Invisible")
        self.assertEqual(context, "")

if __name__ == '__main__':
    unittest.main()
