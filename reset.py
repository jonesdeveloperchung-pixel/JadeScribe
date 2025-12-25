import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from db_manager import reset_database

def main():
    print("⚠️  WARNING: This will DELETE all data in 'data/jade_inventory.db'.")
    choice = input("Are you sure you want to continue? [y/N]: ")
    
    if choice.lower() == 'y':
        print("Resetting database...")
        if reset_database():
            print("✅ Database reset successfully.")
        else:
            print("❌ Database reset failed.")
    else:
        print("Operation cancelled.")

if __name__ == "__main__":
    main()
