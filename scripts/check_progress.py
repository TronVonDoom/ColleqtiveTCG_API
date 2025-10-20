"""
Simple script to monitor the sync progress
"""
import sqlite3
import os
from datetime import datetime

DATABASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pokemon_tcg.db')

def check_progress():
    """Check current sync progress"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        print("=" * 60)
        print("POKEMON TCG DATABASE SYNC PROGRESS")
        print("=" * 60)
        print()
        
        # Check sync status
        cursor.execute("SELECT * FROM sync_status ORDER BY started_at DESC LIMIT 1")
        sync = cursor.fetchone()
        if sync:
            print(f"Last Sync Status: {sync[4]}")  # status column
            print(f"Started: {sync[2]}")  # started_at
            if sync[3]:  # completed_at
                print(f"Completed: {sync[3]}")
            print()
        
        # Count sets
        cursor.execute("SELECT COUNT(*) FROM sets")
        sets_count = cursor.fetchone()[0]
        print(f"Sets synced: {sets_count}")
        
        # Count cards
        cursor.execute("SELECT COUNT(*) FROM cards")
        cards_count = cursor.fetchone()[0]
        print(f"Cards synced: {cards_count}")
        
        # Count by supertype
        cursor.execute("SELECT supertype, COUNT(*) FROM cards GROUP BY supertype")
        supertypes = cursor.fetchall()
        if supertypes:
            print("\nCards by Supertype:")
            for supertype, count in supertypes:
                print(f"  {supertype}: {count}")
        
        # Recent cards
        cursor.execute("SELECT name, set_id, synced_at FROM cards ORDER BY synced_at DESC LIMIT 5")
        recent = cursor.fetchall()
        if recent:
            print("\nMost Recently Synced Cards:")
            for name, set_id, synced_at in recent:
                print(f"  {name} ({set_id}) - {synced_at}")
        
        # Database size
        cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
        size = cursor.fetchone()[0]
        size_mb = size / (1024 * 1024)
        print(f"\nDatabase size: {size_mb:.2f} MB")
        
        print("=" * 60)
        
        conn.close()
        
    except sqlite3.OperationalError as e:
        print(f"Error: {e}")
        print("Database might not be initialized yet or sync is just starting.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    check_progress()
