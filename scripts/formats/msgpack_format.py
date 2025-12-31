"""MessagePack format save functions."""

import asyncio
from pathlib import Path
from typing import List, Dict

try:
    import msgpack
except ImportError:
    msgpack = None



from scripts.models import JapanPostalCode
from scripts.progress_manager import get_progress_manager


async def save_msgpack(data: List[JapanPostalCode], output_path: Path) -> None:
    """Save data as MessagePack file."""
    
    if msgpack is None:
        print("Error: msgpack is not installed. Install it with: pip install msgpack")
        return
    try:
        # Get progress manager
        progress_mgr = get_progress_manager()
        task_id = None
        if progress_mgr:
            task_id = progress_mgr.add_task("all_data.msgpack", total=1)
        # Convert pydantic models to list of dictionaries
        data_dict = [item.model_dump() for item in data]
        
        def _save_msgpack():
            with open(output_path, 'wb') as f:
                msgpack.pack(data_dict, f, use_bin_type=True)
        
        await asyncio.to_thread(_save_msgpack)
        
        if progress_mgr and task_id is not None:
            progress_mgr.update("all_data.msgpack", advance=1)
    except Exception as e:
        print(f"Error saving MessagePack: {e}")
        import sys
        sys.exit(1)


async def save_grouped_msgpack(grouped_data: Dict[str, Dict[str, List[JapanPostalCode]]], datasets_dir: Path) -> None:
    """Save grouped data as MessagePack files with hierarchical structure."""
    if msgpack is None:
        print("Error: msgpack is not installed. Skipping grouped MessagePack files.")
        return
    
    
    semaphore = asyncio.Semaphore(100)
    total_files = sum(1 + len(suffix_dict) for suffix_dict in grouped_data.values())
    
    # Get progress manager
    progress_mgr = get_progress_manager()
    task_id = None
    if progress_mgr:
        task_id = progress_mgr.add_task("MessagePack", total=total_files)
    
    async def save_single_msgpack_file(file_path: Path, data_list):
        async with semaphore:
            def _save():
                file_path.parent.mkdir(parents=True, exist_ok=True)
                data = data_list if isinstance(data_list, list) else [data_list]
                data_dict = [d.model_dump() if hasattr(d, 'model_dump') else d for d in data]
                with open(file_path, 'wb') as f:
                    msgpack.pack(data_dict, f, use_bin_type=True)
            await asyncio.to_thread(_save)
            if progress_mgr and task_id is not None:
                progress_mgr.update("MessagePack", advance=1)
    
    tasks = []
    
    for prefix, suffix_dict in grouped_data.items():
        prefix_dir = datasets_dir / prefix
        prefix_dir.mkdir(parents=True, exist_ok=True)
        
        all_prefix_records = []
        for suffix_records in suffix_dict.values():
            all_prefix_records.extend(suffix_records)
        
        prefix_file = datasets_dir / f"{prefix}.msgpack"
        tasks.append(save_single_msgpack_file(prefix_file, all_prefix_records))
        
        for suffix, records in suffix_dict.items():
            suffix_file = prefix_dir / f"{suffix}.msgpack"
            tasks.append(save_single_msgpack_file(suffix_file, records if len(records) > 1 else records[0]))
    
    await asyncio.gather(*tasks)
    # Progress bar will be closed by main progress manager

