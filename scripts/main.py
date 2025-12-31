#!/usr/bin/env python3
"""
Japan Postal Code Data Converter
Downloads postal code data from Japan Post and converts it to multiple formats.
"""

import asyncio
import csv
import json
import logging
import os
import sys
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import List

import yaml

from models import JapanPostalCode

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def change_to_project_root():
    """Change working directory to project root."""
    script_dir = Path(__file__).parent.absolute()
    project_root = script_dir.parent
    os.chdir(project_root)
    return project_root


def download_zip_file(url: str, output_path: Path) -> None:
    """Download zip file from URL and save to output_path."""
    print(f"Downloading {url}...")
    try:
        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(url, output_path)
        print(f"Downloaded successfully to {output_path}")
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
    Japan Post CSV has no header and uses comma delimiter with fixed positions.
    """
    print(f"Reading CSV data from {csv_path}...")
    data = []
    errors = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row_num, row in enumerate(reader, start=1):
                try:
                    # Map CSV columns to pydantic model fields
                    postal_code = JapanPostalCode(
                        local_government_code=row[0].strip(),
                        old_postal_code=row[1].strip(),
                        postal_code=row[2].strip(),
                        prefecture_name_kana=row[3].strip(),
                        city_name_kana=row[4].strip(),
                        town_name_kana=row[5].strip(),
                        prefecture_name=row[6].strip(),
                        city_name=row[7].strip(),
                        town_name=row[8].strip(),
                        multiple_postal_codes_per_town=row[9].strip(),
                        koaza_numbering=row[10].strip(),
                        has_chome=row[11].strip(),
                        multiple_towns_per_postal_code=row[12].strip(),
                        update_status=row[13].strip(),
                        change_reason=row[14].strip()
                    )
                    data.append(postal_code)
                except Exception as e:
                    errors.append(f"Error parsing row {row_num}: {e}")
                    continue

        print(f"Read {len(data)} records")
        if len(errors) > 0:
            logger.error("\n".join(errors), extra={"prefix": "ERROR:"})
        else:
            return data
    except Exception as e:
        print(f"Error reading CSV: {e}")
        sys.exit(1)


async def save_json(data: List[JapanPostalCode], output_path: Path) -> None:
    """Save data as JSON file using pydantic model fields."""
    print(f"Saving JSON to {output_path}...")
    try:
        # Convert pydantic models to dictionaries using model_dump
        json_data = [item.model_dump() for item in data]
        def _save_json():
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
        await asyncio.to_thread(_save_json)
        print(f"JSON saved successfully")
    except Exception as e:
        print(f"Error saving JSON: {e}")
        sys.exit(1)


async def save_yaml(data: List[JapanPostalCode], output_path: Path) -> None:
    """Save data as YAML file using pydantic model fields."""
    print(f"Saving YAML to {output_path}...")
    try:
        # Convert pydantic models to dictionaries using model_dump
        yaml_data = [item.model_dump() for item in data]
        def _save_yaml():
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(yaml_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        await asyncio.to_thread(_save_yaml)
        print(f"YAML saved successfully")
    except Exception as e:
        print(f"Error saving YAML: {e}")
        sys.exit(1)


async def save_csv(data: List[JapanPostalCode], output_path: Path) -> None:
    """Save data as CSV file using pydantic model fields."""
    print(f"Saving CSV to {output_path}...")
    try:
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
        print(f"CSV saved successfully")
    except Exception as e:
        print(f"Error saving CSV: {e}")
        sys.exit(1)


async def save_xml(data: List[JapanPostalCode], output_path: Path) -> None:
    """Save data as XML file using pydantic model fields."""
    print(f"Saving XML to {output_path}...")
    try:
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
        print(f"XML saved successfully")
    except Exception as e:
        print(f"Error saving XML: {e}")
        sys.exit(1)


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

    # URLs and file paths
    zip_url = "https://www.post.japanpost.jp/zipcode/dl/utf/zip/utf_ken_all.zip"
    zip_path = tmp_dir / "data.zip"
    csv_filename = "utf_ken_all.csv"

    # Download zip file
    download_zip_file(zip_url, zip_path)

    # Extract CSV from zip to tmp directory
    csv_path = extract_csv_from_zip(zip_path, csv_filename, extract_to=tmp_dir)

    # Read CSV data
    data = read_csv_data(csv_path)

    # Convert and save to different formats
    output_files = {
        'json': datasets_dir / "data.json",
        'yaml': datasets_dir / "data.yaml",
        'csv': datasets_dir / "data.csv",
        'xml': datasets_dir / "data.xml"
    }

    # Save to all formats concurrently
    await asyncio.gather(
        save_json(data, output_files['json']),
        save_yaml(data, output_files['yaml']),
        save_csv(data, output_files['csv']),
        save_xml(data, output_files['xml'])
    )

    # Clean up temporary files (optional - comment out if you want to keep them)
    # csv_path.unlink()  # Remove extracted CSV
    # zip_path.unlink()  # Remove downloaded zip

    print("\nConversion completed successfully!")
    print(f"Output files:")
    for fmt, path in output_files.items():
        print(f"  - {path}")


if __name__ == "__main__":
    asyncio.run(main())
