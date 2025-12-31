"""SQLite format save functions."""

import asyncio
import sqlite3
from pathlib import Path
from typing import List

from scripts.models import JapanPostalCode
from scripts.progress_manager import get_progress_manager


async def save_sqlite(data: List[JapanPostalCode], output_path: Path) -> None:
    """Save data as SQLite database."""
    
    try:
        # Get progress manager
        progress_mgr = get_progress_manager()
        task_id = None
        if progress_mgr:
            task_id = progress_mgr.add_task("all_data.db", total=1)
        def _save_sqlite():
            # Remove existing database if it exists
            if output_path.exists():
                output_path.unlink()
            
            # Connect to SQLite database
            conn = sqlite3.connect(output_path)
            cursor = conn.cursor()
            
            # Get field names from pydantic model
            fieldnames = list(JapanPostalCode.model_fields.keys())
            
            # Create table
            columns = ', '.join([f"{field} TEXT" for field in fieldnames])
            cursor.execute(f"CREATE TABLE postal_codes ({columns})")
            
            # Insert data
            data_dict = [item.model_dump() for item in data]
            placeholders = ', '.join(['?' for _ in fieldnames])
            insert_query = f"INSERT INTO postal_codes ({', '.join(fieldnames)}) VALUES ({placeholders})"
            
            for record in data_dict:
                values = [str(record.get(field, '')) for field in fieldnames]
                cursor.execute(insert_query, values)
            
            # Create index on postal_code for faster lookups
            cursor.execute("CREATE INDEX idx_postal_code ON postal_codes(postal_code)")
            
            # Commit and close
            conn.commit()
            conn.close()
        
        await asyncio.to_thread(_save_sqlite)
        
        if progress_mgr and task_id is not None:
            progress_mgr.update("all_data.db", advance=1)
    except Exception as e:
        print(f"Error saving SQLite: {e}")
        import sys
        sys.exit(1)

