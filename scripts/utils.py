"""Utility functions for downloading, extracting, and processing postal code data."""

import os
import sys
import urllib.request
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import List, Dict

try:
    import pandas as pd
except ImportError:
    pd = None

from models import JapanPostalCode
from scripts.progress_manager import get_progress_manager


def change_to_project_root():
    """Change working directory to project root."""
    script_dir = Path(__file__).parent.absolute()
    project_root = script_dir.parent
    os.chdir(project_root)
    return project_root


def download_zip_file(url: str, output_path: Path) -> None:
    """Download zip file from URL and save to output_path using rich progress bar."""
    try:
        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        from urllib.request import urlopen
        response = urlopen(url)
        total_size = int(response.headers.get('Content-Length', 0))
        
        # Use rich progress manager
        progress_mgr = get_progress_manager()
        task_id = None
        if progress_mgr:
            task_id = progress_mgr.add_task("Download", total=total_size, show_bytes=True)
        
        with open(output_path, 'wb') as f:
            while True:
                chunk = response.read(8192)
                if not chunk:
                    break
                f.write(chunk)
                if progress_mgr and task_id is not None:
                    progress_mgr.update("Download", advance=len(chunk))
        
        file_size = os.path.getsize(output_path) / (1024 * 1024)
    except Exception as e:
        print(f"Error downloading file: {e}")
        sys.exit(1)


def extract_csv_from_zip(zip_path: Path, csv_filename: str = "utf_ken_all.csv", extract_to: Path = None) -> Path:
    """Extract CSV file from zip archive."""
    print(f"Extracting {csv_filename} from {zip_path}...")
    try:
        extract_dir = extract_to if extract_to else zip_path.parent
        extract_dir.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # List all files in zip
            file_list = zip_ref.namelist()
            print(f"Files in zip: {file_list}")
            
            # Extract the CSV file
            zip_ref.extract(csv_filename, extract_dir)
            csv_path = extract_dir / csv_filename
            print(f"Extracted to {csv_path}")
            return csv_path
    except Exception as e:
        print(f"Error extracting CSV: {e}")
        sys.exit(1)


def read_csv_data(csv_path: Path) -> List[JapanPostalCode]:
    """
    Read CSV file and return list of JapanPostalCode pydantic models.
    Uses pandas for fast CSV reading (5-10x faster than standard csv module).
    """
    file_size = os.path.getsize(csv_path) / (1024 * 1024)  # Size in MB
    print(f"Reading CSV data from {csv_path}...")
    print(f"  File size: {file_size:.2f} MB")
    
    if pd is None:
        print("  Warning: pandas not available, falling back to standard csv module")
        return _read_csv_data_slow(csv_path)
    
    try:
        # Use pandas for fast CSV reading
        print("  Using pandas for fast CSV reading...")
        df = pd.read_csv(
            csv_path,
            header=None,
            names=[
                'local_government_code', 'old_postal_code', 'postal_code',
                'prefecture_name_kana', 'city_name_kana', 'town_name_kana',
                'prefecture_name', 'city_name', 'town_name',
                'multiple_postal_codes_per_town', 'koaza_numbering', 'has_chome',
                'multiple_towns_per_postal_code', 'update_status', 'change_reason'
            ],
            dtype=str,
            na_filter=False,  # Don't process NaN, faster
            engine='c',  # Use C engine for speed
            memory_map=True  # Memory map for large files
        )
        
        print(f"  Loaded {len(df)} rows into DataFrame")
        
        # Batch convert to Pydantic models
        data = []
        errors = []
        
        # Use rich progress manager
        progress_mgr = get_progress_manager()
        task_id = None
        if progress_mgr:
            task_id = progress_mgr.add_task("Reading CSV", total=len(df))
        
        iterator = df.itertuples(index=False)
        for row in iterator:
            try:
                # Strip all string fields to remove trailing/leading whitespace
                postal_code = JapanPostalCode(
                    local_government_code=row.local_government_code.strip() if row.local_government_code else None,
                    old_postal_code=row.old_postal_code.strip() if row.old_postal_code else None,
                    postal_code=row.postal_code.strip() if row.postal_code else None,
                    prefecture_name_kana=row.prefecture_name_kana.strip() if row.prefecture_name_kana else None,
                    city_name_kana=row.city_name_kana.strip() if row.city_name_kana else None,
                    town_name_kana=row.town_name_kana.strip() if row.town_name_kana else None,
                    prefecture_name=row.prefecture_name.strip() if row.prefecture_name else None,
                    city_name=row.city_name.strip() if row.city_name else None,
                    town_name=row.town_name.strip() if row.town_name else None,
                    multiple_postal_codes_per_town=row.multiple_postal_codes_per_town.strip() if row.multiple_postal_codes_per_town else None,
                    koaza_numbering=row.koaza_numbering.strip() if row.koaza_numbering else None,
                    has_chome=row.has_chome.strip() if row.has_chome else None,
                    multiple_towns_per_postal_code=row.multiple_towns_per_postal_code.strip() if row.multiple_towns_per_postal_code else None,
                    update_status=row.update_status.strip() if row.update_status else None,
                    change_reason=row.change_reason.strip() if row.change_reason else None
                )
                data.append(postal_code)
                if progress_mgr and task_id is not None:
                    progress_mgr.update("Reading CSV", advance=1)
            except Exception as e:
                errors.append(f"Error parsing row: {e}")
                if progress_mgr and task_id is not None:
                    progress_mgr.update("Reading CSV", advance=1)
                continue
        
        print(f"  Successfully read {len(data)} records")
        if len(errors) > 0:
            print(f"  Warning: {len(errors)} rows had parsing errors")
            if len(errors) <= 10:
                for error in errors:
                    print(f"    - {error}")
            else:
                print(f"    (Showing first 10 errors, {len(errors) - 10} more...)")
                for error in errors[:10]:
                    print(f"    - {error}")
        return data
    except Exception as e:
        print(f"Error reading CSV with pandas: {e}")
        print("  Falling back to standard csv module...")
        return _read_csv_data_slow(csv_path)


def _read_csv_data_slow(csv_path: Path) -> List[JapanPostalCode]:
    """Fallback: Read CSV using standard csv module."""
    import csv
    data = []
    errors = []
    try:
        # Count total lines first
        with open(csv_path, 'r', encoding='utf-8') as f:
            total_lines = sum(1 for _ in f)
        
        # Use rich progress manager
        progress_mgr = get_progress_manager()
        task_id = None
        if progress_mgr:
            task_id = progress_mgr.add_task("Reading CSV", total=total_lines)
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row_num, row in enumerate(reader, start=1):
                try:
                    # Strip all fields and handle empty strings
                    postal_code = JapanPostalCode(
                        local_government_code=row[0].strip() if row[0] else None,
                        old_postal_code=row[1].strip() if row[1] else None,
                        postal_code=row[2].strip() if row[2] else None,
                        prefecture_name_kana=row[3].strip() if row[3] else None,
                        city_name_kana=row[4].strip() if row[4] else None,
                        town_name_kana=row[5].strip() if row[5] else None,
                        prefecture_name=row[6].strip() if row[6] else None,
                        city_name=row[7].strip() if row[7] else None,
                        town_name=row[8].strip() if row[8] else None,
                        multiple_postal_codes_per_town=row[9].strip() if row[9] else None,
                        koaza_numbering=row[10].strip() if row[10] else None,
                        has_chome=row[11].strip() if row[11] else None,
                        multiple_towns_per_postal_code=row[12].strip() if row[12] else None,
                        update_status=row[13].strip() if row[13] else None,
                        change_reason=row[14].strip() if row[14] else None
                    )
                    data.append(postal_code)
                    if progress_mgr and task_id is not None:
                        progress_mgr.update("Reading CSV", advance=1)
                except Exception as e:
                    errors.append(f"Error parsing row {row_num}: {e}")
                    if progress_mgr and task_id is not None:
                        progress_mgr.update("Reading CSV", advance=1)
                    continue
        
        print(f"  Successfully read {len(data)} records")
        if len(errors) > 0:
            print(f"  Warning: {len(errors)} rows had parsing errors")
        return data
    except Exception as e:
        print(f"Error reading CSV: {e}")
        sys.exit(1)


def group_by_postal_code_prefix(data: List[JapanPostalCode]) -> Dict[str, Dict[str, List[JapanPostalCode]]]:
    """
    Group postal code data by prefix (first 3 digits) and suffix (last 4 digits).
    Uses defaultdict for faster grouping (10-20% faster).
    
    Returns:
        Dict[str, Dict[str, List[JapanPostalCode]]]: 
        {
            "176": {
                "0005": [record1, record2, ...],  # All records for 1760005
                "0006": [record3, ...],            # All records for 1760006
                ...
            },
            ...
        }
    """
    print(f"Grouping {len(data)} records by postal code prefix...")
    # Use defaultdict to avoid frequent key existence checks
    grouped = defaultdict(lambda: defaultdict(list))
    skipped_count = 0
    
    for record in data:
        postal_code = record.postal_code
        if len(postal_code) != 7:
            skipped_count += 1
            continue
        
        prefix = postal_code[:3]  # First 3 digits
        suffix = postal_code[3:]   # Last 4 digits
        grouped[prefix][suffix].append(record)
    
    # Convert to regular dict for return (maintains compatibility)
    result = {k: dict(v) for k, v in grouped.items()}
    
    total_suffixes = sum(len(suffix_dict) for suffix_dict in result.values())
    print(f"Grouping completed: {len(result)} prefix groups, {total_suffixes} unique postal codes")
    if skipped_count > 0:
        print(f"Warning: {skipped_count} records skipped (invalid postal code length)")
    
    return result

