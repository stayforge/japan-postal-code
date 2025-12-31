"""Parquet format save functions."""

import asyncio
from pathlib import Path
from typing import List, Dict

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
except ImportError:
    pa = None
    pq = None



from scripts.models import JapanPostalCode
from scripts.progress_manager import get_progress_manager


async def save_parquet(data: List[JapanPostalCode], output_path: Path) -> None:
    """Save data as Parquet file using pyarrow."""
    
    if pq is None:
        print("Error: pyarrow is not installed. Install it with: pip install pyarrow")
        return
    try:
        # Get progress manager
        progress_mgr = get_progress_manager()
        task_id = None
        if progress_mgr:
            task_id = progress_mgr.add_task("all_data.parquet", total=1)
        # Convert pydantic models to list of dictionaries
        data_dict = [item.model_dump() for item in data]
        
        def _save_parquet():
            # Convert to Arrow table
            table = pa.Table.from_pylist(data_dict)
            # Write to Parquet file
            pq.write_table(table, output_path, compression='snappy')
        
        await asyncio.to_thread(_save_parquet)
        
        if progress_mgr and task_id is not None:
            progress_mgr.update("all_data.parquet", advance=1)
    except Exception as e:
        print(f"Error saving Parquet: {e}")
        import sys
        sys.exit(1)


async def save_grouped_parquet(grouped_data: Dict[str, Dict[str, List[JapanPostalCode]]], datasets_dir: Path) -> None:
    """Save grouped data as Parquet files with hierarchical structure."""
    if pq is None:
        print("Error: pyarrow is not installed. Skipping grouped Parquet files.")
        return
    
    
    semaphore = asyncio.Semaphore(50)  # Lower limit for Parquet due to memory usage
    total_files = sum(1 + len(suffix_dict) for suffix_dict in grouped_data.values())
    
    # Get progress manager for stable multi-line progress bars
    progress_mgr = get_progress_manager()
    task_id = None
    if progress_mgr:
        task_id = progress_mgr.add_task("Parquet", total=total_files)
    
    async def save_single_parquet_file(file_path: Path, records_list):
        async with semaphore:
            def _save():
                file_path.parent.mkdir(parents=True, exist_ok=True)
                records = records_list if isinstance(records_list, list) else [records_list]
                data_dict = [r.model_dump() if hasattr(r, 'model_dump') else r for r in records]
                table = pa.Table.from_pylist(data_dict)
                pq.write_table(table, file_path, compression='snappy')
            await asyncio.to_thread(_save)
            if progress_mgr and task_id is not None:
                progress_mgr.update("Parquet", advance=1)
    
    tasks = []
    
    for prefix, suffix_dict in grouped_data.items():
        prefix_dir = datasets_dir / prefix
        prefix_dir.mkdir(parents=True, exist_ok=True)
        
        all_prefix_records = []
        for suffix_records in suffix_dict.values():
            all_prefix_records.extend(suffix_records)
        
        prefix_file = datasets_dir / f"{prefix}.parquet"
        tasks.append(save_single_parquet_file(prefix_file, all_prefix_records))
        
        for suffix, records in suffix_dict.items():
            suffix_file = prefix_dir / f"{suffix}.parquet"
            tasks.append(save_single_parquet_file(suffix_file, records if len(records) > 1 else records[0]))
    
    await asyncio.gather(*tasks)
    # Progress bar will be closed by main progress manager

