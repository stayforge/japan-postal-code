"""CSV format save functions."""

import asyncio
import csv
from pathlib import Path
from typing import List, Dict

from scripts.models import JapanPostalCode
from scripts.progress_manager import get_progress_manager


async def save_csv(data: List[JapanPostalCode], output_path: Path) -> None:
    """Save data as CSV file using pydantic model fields."""
    
    try:
        # Get progress manager
        progress_mgr = get_progress_manager()
        task_id = None
        if progress_mgr:
            task_id = progress_mgr.add_task("all_data.csv", total=1)
        if not data:
            print("No data to save")
            return

        # Get field names from pydantic model class
        fieldnames = list(JapanPostalCode.model_fields.keys())
        # Convert pydantic models to dictionaries
        csv_data = [item.model_dump() for item in data]

        def _save_csv():
            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_data)
        await asyncio.to_thread(_save_csv)
        
        if progress_mgr and task_id is not None:
            progress_mgr.update("all_data.csv", advance=1)
    except Exception as e:
        print(f"Error saving CSV: {e}")
        import sys
        sys.exit(1)


async def save_grouped_csv(grouped_data: Dict[str, Dict[str, List[JapanPostalCode]]], datasets_dir: Path) -> None:
    """Save grouped data as CSV files with hierarchical structure."""
    semaphore = asyncio.Semaphore(100)
    fieldnames = list(JapanPostalCode.model_fields.keys())
    saved_files = 0
    total_files = sum(1 + len(suffix_dict) for suffix_dict in grouped_data.values())
    
    # Get progress manager for stable multi-line progress bars
    progress_mgr = get_progress_manager()
    task_id = None
    if progress_mgr:
        task_id = progress_mgr.add_task("CSV", total=total_files)
    
    async def save_single_csv_file(file_path: Path, csv_data_list):
        nonlocal saved_files
        async with semaphore:
            def _save():
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    # Handle both single dict and list of dicts
                    if isinstance(csv_data_list, list):
                        writer.writerows(csv_data_list)
                    else:
                        writer.writerow(csv_data_list)
            await asyncio.to_thread(_save)
            saved_files += 1
            if progress_mgr and task_id is not None:
                progress_mgr.update("CSV", advance=1)
    
    tasks = []
    
    for prefix, suffix_dict in grouped_data.items():
        prefix_dir = datasets_dir / prefix
        prefix_dir.mkdir(parents=True, exist_ok=True)
        
        all_prefix_records = []
        for suffix_records in suffix_dict.values():
            all_prefix_records.extend(suffix_records)
        
        prefix_file = datasets_dir / f"{prefix}.csv"
        prefix_data = [record.model_dump() for record in all_prefix_records]
        tasks.append(save_single_csv_file(prefix_file, prefix_data))
        
        for suffix, records in suffix_dict.items():
            suffix_file = prefix_dir / f"{suffix}.csv"
            suffix_data = [record.model_dump() for record in records]
            tasks.append(save_single_csv_file(suffix_file, suffix_data if len(suffix_data) > 1 else suffix_data[0]))
    
    await asyncio.gather(*tasks)
    # Progress bar will be closed by main progress manager

