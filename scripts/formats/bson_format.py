"""BSON format save functions."""

import asyncio
from pathlib import Path
from typing import List, Dict

try:
    import bson
except ImportError:
    bson = None



from scripts.models import JapanPostalCode
from scripts.progress_manager import get_progress_manager


async def save_bson(data: List[JapanPostalCode], output_path: Path) -> None:
    """Save data as BSON file."""
    
    if bson is None:
        print("Error: bson is not installed. Install it with: pip install pymongo")
        return
    try:
        # Get progress manager
        progress_mgr = get_progress_manager()
        task_id = None
        if progress_mgr:
            task_id = progress_mgr.add_task("all_data.bson", total=1)
        # Convert pydantic models to list of dictionaries
        data_dict = [item.model_dump() for item in data]
        
        def _save_bson():
            with open(output_path, 'wb') as f:
                bson_data = bson.encode({"postal_codes": data_dict})
                f.write(bson_data)
        
        await asyncio.to_thread(_save_bson)
        
        if progress_mgr and task_id is not None:
            progress_mgr.update("all_data.bson", advance=1)
    except Exception as e:
        print(f"Error saving BSON: {e}")
        import sys
        sys.exit(1)


async def save_grouped_bson(grouped_data: Dict[str, Dict[str, List[JapanPostalCode]]], datasets_dir: Path) -> None:
    """Save grouped data as BSON files with hierarchical structure."""
    if bson is None:
        print("Error: bson is not installed. Skipping grouped BSON files.")
        return
    
    
    semaphore = asyncio.Semaphore(100)
    total_files = sum(1 + len(suffix_dict) for suffix_dict in grouped_data.values())
    
    # Get progress manager
    progress_mgr = get_progress_manager()
    task_id = None
    if progress_mgr:
        task_id = progress_mgr.add_task("BSON", total=total_files)
    
    async def save_single_bson_file(file_path: Path, records_list):
        async with semaphore:
            def _save():
                file_path.parent.mkdir(parents=True, exist_ok=True)
                records = records_list if isinstance(records_list, list) else [records_list]
                data_dict = [r.model_dump() if hasattr(r, 'model_dump') else r for r in records]
                with open(file_path, 'wb') as f:
                    bson_data = bson.encode({"postal_codes": data_dict})
                    f.write(bson_data)
            await asyncio.to_thread(_save)
            if progress_mgr and task_id is not None:
                progress_mgr.update("BSON", advance=1)
    
    tasks = []
    
    for prefix, suffix_dict in grouped_data.items():
        prefix_dir = datasets_dir / prefix
        prefix_dir.mkdir(parents=True, exist_ok=True)
        
        all_prefix_records = []
        for suffix_records in suffix_dict.values():
            all_prefix_records.extend(suffix_records)
        
        prefix_file = datasets_dir / f"{prefix}.bson"
        tasks.append(save_single_bson_file(prefix_file, all_prefix_records))
        
        for suffix, records in suffix_dict.items():
            suffix_file = prefix_dir / f"{suffix}.bson"
            tasks.append(save_single_bson_file(suffix_file, records if len(records) > 1 else records[0]))
    
    await asyncio.gather(*tasks)
    # Progress bar will be closed by main progress manager

