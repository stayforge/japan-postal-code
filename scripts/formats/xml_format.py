"""XML format save functions."""

import asyncio
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict



from scripts.models import JapanPostalCode
from scripts.progress_manager import get_progress_manager


async def save_xml(data: List[JapanPostalCode], output_path: Path) -> None:
    """Save data as XML file using pydantic model fields."""
    
    try:
        # Get progress manager
        progress_mgr = get_progress_manager()
        task_id = None
        if progress_mgr:
            task_id = progress_mgr.add_task("all_data.xml", total=1)
        root = ET.Element('postal_codes')
        for record in data:
            record_elem = ET.SubElement(root, 'record')
            # Convert pydantic model to dictionary
            record_dict = record.model_dump()
            for key, value in record_dict.items():
                # Use field name directly (already safe for XML)
                field_elem = ET.SubElement(record_elem, key)
                field_elem.text = str(value) if value else ''
        
        tree = ET.ElementTree(root)
        ET.indent(tree, space='  ')
        def _save_xml():
            tree.write(output_path, encoding='utf-8', xml_declaration=True)
        await asyncio.to_thread(_save_xml)
        
        if progress_mgr and task_id is not None:
            progress_mgr.update("all_data.xml", advance=1)
    except Exception as e:
        print(f"Error saving XML: {e}")
        import sys
        sys.exit(1)


async def save_grouped_xml(grouped_data: Dict[str, Dict[str, List[JapanPostalCode]]], datasets_dir: Path) -> None:
    """Save grouped data as XML files with hierarchical structure."""
    semaphore = asyncio.Semaphore(100)
    total_files = sum(1 + len(suffix_dict) for suffix_dict in grouped_data.values())
    
    # Get progress manager for stable multi-line progress bars
    progress_mgr = get_progress_manager()
    task_id = None
    if progress_mgr:
        task_id = progress_mgr.add_task("XML", total=total_files)
    
    async def save_single_xml_file(file_path: Path, records_list):
        async with semaphore:
            def _save():
                file_path.parent.mkdir(parents=True, exist_ok=True)
                root = ET.Element('postal_codes')
                # Handle both single record and list of records
                records = records_list if isinstance(records_list, list) else [records_list]
                for record in records:
                    record_elem = ET.SubElement(root, 'record')
                    record_dict = record.model_dump() if hasattr(record, 'model_dump') else record
                    for key, value in record_dict.items():
                        field_elem = ET.SubElement(record_elem, key)
                        field_elem.text = str(value) if value else ''
                
                tree = ET.ElementTree(root)
                ET.indent(tree, space='  ')
                tree.write(file_path, encoding='utf-8', xml_declaration=True)
            await asyncio.to_thread(_save)
            if progress_mgr and task_id is not None:
                progress_mgr.update("XML", advance=1)
    
    tasks = []
    
    for prefix, suffix_dict in grouped_data.items():
        prefix_dir = datasets_dir / prefix
        prefix_dir.mkdir(parents=True, exist_ok=True)
        
        all_prefix_records = []
        for suffix_records in suffix_dict.values():
            all_prefix_records.extend(suffix_records)
        
        prefix_file = datasets_dir / f"{prefix}.xml"
        tasks.append(save_single_xml_file(prefix_file, all_prefix_records))
        
        for suffix, records in suffix_dict.items():
            suffix_file = prefix_dir / f"{suffix}.xml"
            tasks.append(save_single_xml_file(suffix_file, records if len(records) > 1 else records[0]))
    
    await asyncio.gather(*tasks)
    # Progress bar will be closed by main progress manager

