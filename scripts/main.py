#!/usr/bin/env python3
"""
Japan Postal Code Data Converter
Downloads postal code data from Japan Post and converts it to multiple formats.
"""

import asyncio
import os
import sys
import time
from pathlib import Path

# Add project root to Python path so imports work
script_dir = Path(__file__).parent.absolute()
project_root = script_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from scripts.progress_manager import get_progress_manager, reset_progress_manager
from scripts.formats.bson_format import save_bson, save_grouped_bson
from scripts.formats.csv_format import save_csv, save_grouped_csv
from scripts.formats.feather_format import save_feather, save_grouped_feather
# Import format modules
from scripts.formats.json_format import save_json, save_grouped_json
from scripts.formats.msgpack_format import save_msgpack, save_grouped_msgpack
from scripts.formats.ndjson_format import save_ndjson, save_grouped_ndjson
from scripts.formats.parquet_format import save_parquet, save_grouped_parquet
from scripts.formats.sqlite_format import save_sqlite
from scripts.formats.toml_format import save_toml, save_grouped_toml
from scripts.formats.xml_format import save_xml, save_grouped_xml
from scripts.formats.yaml_format import save_yaml, save_grouped_yaml
# Import utility functions
from scripts.utils import (
    change_to_project_root,
    download_zip_file,
    extract_csv_from_zip,
    read_csv_data,
    group_by_postal_code_prefix
)


async def main():
    """Main function to download, extract, and convert postal code data."""
    # Change to project root
    project_root = change_to_project_root()
    datasets_dir = project_root / "datasets"
    tmp_dir = project_root / "tmp"

    # Create directories if they don't exist
    datasets_dir.mkdir(exist_ok=True)
    tmp_dir.mkdir(exist_ok=True)

    print(f"Working directory: {project_root}")
    print(f"Datasets directory: {datasets_dir}")
    print(f"Temporary directory: {tmp_dir}")

    # Initialize progress manager early for all operations
    progress_mgr = get_progress_manager()
    
    # URLs and file paths
    zip_url = "https://www.post.japanpost.jp/zipcode/dl/utf/zip/utf_ken_all.zip"
    zip_path = tmp_dir / "data.zip"
    csv_filename = "utf_ken_all.csv"
    
    # Download zip file
    print("\n" + "=" * 60)
    print("Step 1: Downloading postal code data")
    print("=" * 60)
    download_zip_file(zip_url, zip_path)
    
    # Extract CSV from zip to tmp directory
    print("\n" + "=" * 60)
    print("Step 2: Extracting and reading CSV data")
    print("=" * 60)
    csv_path = extract_csv_from_zip(zip_path, csv_filename, extract_to=tmp_dir)
    
    # Read CSV data
    data = read_csv_data(csv_path)
    print(f"\nCSV Reading Statistics:")
    print(f"  - Total records loaded: {len(data)}")

    # Group data by postal code prefix
    print("\n" + "=" * 60)
    print("Step 3: Grouping data by postal code prefix")
    print("=" * 60)
    grouped_data = group_by_postal_code_prefix(data)

    # Calculate statistics
    total_suffixes = sum(len(suffix_dict) for suffix_dict in grouped_data.values())
    total_grouped_records = sum(
        sum(len(records) for records in suffix_dict.values())
        for suffix_dict in grouped_data.values()
    )
    print(f"\nGrouping Statistics:")
    print(f"  - Total prefix groups: {len(grouped_data)}")
    print(f"  - Total unique postal codes: {total_suffixes}")
    print(f"  - Total records in grouped data: {total_grouped_records}")
    print(f"  - Average records per prefix: {total_grouped_records / len(grouped_data):.1f}")
    
    # Convert and save to different formats
    output_files = {
        'json': datasets_dir / "all_data.json",
        'yaml': datasets_dir / "all_data.yaml",
        'csv': datasets_dir / "all_data.csv",
        'xml': datasets_dir / "all_data.xml",
        'parquet': datasets_dir / "all_data.parquet",
        'msgpack': datasets_dir / "all_data.msgpack",
        'ndjson': datasets_dir / "all_data.ndjson",
        'toml': datasets_dir / "all_data.toml",
        'feather': datasets_dir / "all_data.feather",
        'bson': datasets_dir / "all_data.bson",
        'sqlite': datasets_dir / "all_data.db"
    }

    # Save to all formats concurrently (both full data and grouped)
    print("\n" + "=" * 60)
    print("Step 4: Saving data to all formats")
    print("=" * 60)
    print(f"Saving {len(output_files)} full data files and grouped files for {len(grouped_data)} prefix groups...")
    print("This may take a while. Processing in parallel...\n")

    start_time = time.time()

    try:
        await asyncio.gather(
        # Save full data files
        save_json(data, output_files['json']),
        save_yaml(data, output_files['yaml']),
        save_csv(data, output_files['csv']),
        save_xml(data, output_files['xml']),
        save_parquet(data, output_files['parquet']),
        save_msgpack(data, output_files['msgpack']),
        save_ndjson(data, output_files['ndjson']),
        save_toml(data, output_files['toml']),
        save_feather(data, output_files['feather']),
        save_bson(data, output_files['bson']),
        save_sqlite(data, output_files['sqlite']),
        # Save grouped data files
        save_grouped_json(grouped_data, datasets_dir),
        # save_grouped_yaml(grouped_data, datasets_dir),
        # save_grouped_csv(grouped_data, datasets_dir),
        # save_grouped_xml(grouped_data, datasets_dir),
        # save_grouped_parquet(grouped_data, datasets_dir),
        # save_grouped_msgpack(grouped_data, datasets_dir),
        # save_grouped_ndjson(grouped_data, datasets_dir),
        # save_grouped_toml(grouped_data, datasets_dir),
        # save_grouped_feather(grouped_data, datasets_dir),
        # save_grouped_bson(grouped_data, datasets_dir)
        )
    finally:
        # Close progress manager
        if progress_mgr:
            progress_mgr.close()
            reset_progress_manager()

    elapsed_time = time.time() - start_time
    print(f"\nAll files saved in {elapsed_time:.2f} seconds")

    # Clean up temporary files (optional - comment out if you want to keep them)
    # csv_path.unlink()  # Remove extracted CSV
    # zip_path.unlink()  # Remove downloaded zip

    print("\n" + "=" * 60)
    print("Conversion completed successfully!")
    print("=" * 60)

    # Count generated files
    try:
        all_files = os.listdir(datasets_dir)
        prefix_files_count = sum(
            1 for f in all_files if os.path.isfile(datasets_dir / f) and not f.startswith('all_data'))
        suffix_dirs = [d for d in all_files if os.path.isdir(datasets_dir / d) and d.isdigit()]
        suffix_files_count = sum(
            len([f for f in os.listdir(datasets_dir / d) if os.path.isfile(datasets_dir / d / f)])
            for d in suffix_dirs
        )

        print(f"\nSummary:")
        print(f"  - Full data files: {len(output_files)}")
        print(f"  - Prefix group files: {prefix_files_count}")
        print(f"  - Suffix detail files: {suffix_files_count}")
        print(f"  - Total grouped files: {prefix_files_count + suffix_files_count}")
        print(f"  - Total output files: {len(output_files) + prefix_files_count + suffix_files_count}")

        print(f"\nFull data files (sizes):")
        for fmt, path in output_files.items():
            if path.exists():
                file_size = os.path.getsize(path)
                size_mb = file_size / (1024 * 1024)
                print(f"  - {path.name}: {size_mb:.2f} MB")
            else:
                print(f"  - {path.name}: (not created)")

        print(f"\nOutput directory: {datasets_dir}")
        print(f"Grouped data structure: datasets/<prefix>.<ext> and datasets/<prefix>/<suffix>.<ext>")
        print(f"Example URLs:")
        print(f"  - https://stayforge.github.io/japan-postal-code/datasets/176.json")
        print(f"  - https://stayforge.github.io/japan-postal-code/datasets/176/0005.json")
    except Exception as e:
        print(f"\nNote: Could not calculate file statistics: {e}")
        print(f"Output directory: {datasets_dir}")


if __name__ == "__main__":
    asyncio.run(main())
