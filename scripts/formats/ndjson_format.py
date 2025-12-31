"""NDJSON format save functions."""

import asyncio
import json
from pathlib import Path
from typing import List, Dict



from scripts.models import JapanPostalCode
from scripts.progress_manager import get_progress_manager


async def save_ndjson(data: List[JapanPostalCode], output_path: Path) -> None:
    """Save data as NDJSON (Newline-Delimited JSON) file."""
    
    try:
        # Get progress manager
        progress_mgr = get_progress_manager()
        task_id = None
        if progress_mgr:
            task_id = progress_mgr.add_task("all_data.ndjson", total=1)
        # Batch convert to dicts first for better performance
        try:
            import orjson
            USE_ORJSON = True
        except ImportError:
            import json
            USE_ORJSON = False
        
        def _save_ndjson():
            with open(output_path, 'w', encoding='utf-8') as f:
                # Pre-convert all to dicts in batch
                data_dicts = [item.model_dump() for item in data]
                for item_dict in data_dicts:
                    if USE_ORJSON:
                        # orjson is faster
                        json_line = orjson.dumps(item_dict).decode('utf-8')
                    else:
                        json_line = json.dumps(item_dict, ensure_ascii=False)
                    f.write(json_line + '\n')
        
        await asyncio.to_thread(_save_ndjson)
        
        if progress_mgr and task_id is not None:
            progress_mgr.update("all_data.ndjson", advance=1)
    except Exception as e:
        print(f"Error saving NDJSON: {e}")
        import sys
        sys.exit(1)


async def save_grouped_ndjson(grouped_data: Dict[str, Dict[str, List[JapanPostalCode]]], datasets_dir: Path) -> None:
    """Save grouped data as NDJSON files with hierarchical structure."""
    semaphore = asyncio.Semaphore(100)
    total_files = sum(1 + len(suffix_dict) for suffix_dict in grouped_data.values())
    
    # Get progress manager for stable multi-line progress bars
    progress_mgr = get_progress_manager()
    task_id = None
    if progress_mgr:
        task_id = progress_mgr.add_task("NDJSON", total=total_files)
    
    async def save_single_ndjson_file(file_path: Path, records_list):
        async with semaphore:
            def _save():
                file_path.parent.mkdir(parents=True, exist_ok=True)
                records = records_list if isinstance(records_list, list) else [records_list]
                # Batch convert to dicts first for better performance
                try:
                    import orjson
                    USE_ORJSON = True
                except ImportError:
                    USE_ORJSON = False
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    # Pre-convert all to dicts in batch
                    record_dicts = [r.model_dump() if hasattr(r, 'model_dump') else r for r in records]
                    for record_dict in record_dicts:
                        if USE_ORJSON:
                            json_line = orjson.dumps(record_dict).decode('utf-8')
                        else:
                            json_line = json.dumps(record_dict, ensure_ascii=False)
                        f.write(json_line + '\n')
            await asyncio.to_thread(_save)
            if progress_mgr and task_id is not None:
                progress_mgr.update("NDJSON", advance=1)
    
    tasks = []
    
    for prefix, suffix_dict in grouped_data.items():
        prefix_dir = datasets_dir / prefix
        prefix_dir.mkdir(parents=True, exist_ok=True)
        
        all_prefix_records = []
        for suffix_records in suffix_dict.values():
            all_prefix_records.extend(suffix_records)
        
        prefix_file = datasets_dir / f"{prefix}.ndjson"
        tasks.append(save_single_ndjson_file(prefix_file, all_prefix_records))
        
        for suffix, records in suffix_dict.items():
            suffix_file = prefix_dir / f"{suffix}.ndjson"
            tasks.append(save_single_ndjson_file(suffix_file, records if len(records) > 1 else records[0]))
    
    await asyncio.gather(*tasks)
    # Progress bar will be closed by main progress manager

