"""JSON format save functions."""

import asyncio
from pathlib import Path
from typing import List, Dict

try:
    import orjson
    USE_ORJSON = True
except ImportError:
    import json
    USE_ORJSON = False

from scripts.models import JapanPostalCode
from scripts.progress_manager import get_progress_manager


async def save_json(data: List[JapanPostalCode], output_path: Path) -> None:
    """Save data as JSON file using orjson for speed (2-3x faster)."""
    try:
        # Get progress manager
        progress_mgr = get_progress_manager()
        task_id = None
        if progress_mgr:
            task_id = progress_mgr.add_task("all_data.json", total=1)
        
        # Batch convert pydantic models to dictionaries
        json_data = [item.model_dump() for item in data]
        
        def _save_json():
            if USE_ORJSON:
                # orjson is 2-3x faster than standard json
                with open(output_path, 'wb') as f:
                    f.write(orjson.dumps(json_data, option=orjson.OPT_INDENT_2))
            else:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
        await asyncio.to_thread(_save_json)
        
        if progress_mgr and task_id is not None:
            progress_mgr.update("all_data.json", advance=1)
    except Exception as e:
        print(f"Error saving JSON: {e}")
        import sys
        sys.exit(1)


async def save_grouped_json(grouped_data: Dict[str, Dict[str, List[JapanPostalCode]]], datasets_dir: Path) -> None:
    """Save grouped data as JSON files with hierarchical structure."""
    # Semaphore to limit concurrent file operations
    semaphore = asyncio.Semaphore(100)
    saved_files = 0
    total_files = sum(1 + len(suffix_dict) for suffix_dict in grouped_data.values())
    
    # Get progress manager for stable multi-line progress bars
    progress_mgr = get_progress_manager()
    task_id = None
    if progress_mgr:
        task_id = progress_mgr.add_task("JSON", total=total_files)
    
    async def save_single_json_file(file_path: Path, json_data):
        """Save a single JSON file with semaphore control."""
        nonlocal saved_files
        async with semaphore:
            def _save():
                file_path.parent.mkdir(parents=True, exist_ok=True)
                if USE_ORJSON:
                    # orjson is faster and writes bytes
                    with open(file_path, 'wb') as f:
                        f.write(orjson.dumps(json_data, option=orjson.OPT_INDENT_2))
                else:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(json_data, f, ensure_ascii=False, indent=2)
            await asyncio.to_thread(_save)
            saved_files += 1
            if progress_mgr and task_id is not None:
                progress_mgr.update("JSON", advance=1)
    
    tasks = []
    
    # Process each prefix group
    for prefix, suffix_dict in grouped_data.items():
        prefix_dir = datasets_dir / prefix
        prefix_dir.mkdir(parents=True, exist_ok=True)
        
        # Collect all records for this prefix
        all_prefix_records = []
        for suffix_records in suffix_dict.values():
            all_prefix_records.extend(suffix_records)
        
        # Save prefix-level file (e.g., 176.json)
        # Batch convert to dicts for better performance
        prefix_file = datasets_dir / f"{prefix}.json"
        prefix_data = [record.model_dump() for record in all_prefix_records]
        tasks.append(save_single_json_file(prefix_file, prefix_data))
        
        # Save suffix-level files (e.g., 176/0005.json)
        for suffix, records in suffix_dict.items():
            suffix_file = prefix_dir / f"{suffix}.json"
            # Batch convert to dicts
            suffix_data = [record.model_dump() for record in records]
            tasks.append(save_single_json_file(suffix_file, suffix_data if len(suffix_data) > 1 else suffix_data[0]))
    
    await asyncio.gather(*tasks)
    # Progress bar will be closed by main progress manager
    # print(f"Grouped JSON files saved successfully: {saved_files} files")

