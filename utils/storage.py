import os
import json
import glob
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Create 'data' directory if it doesn't exist
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / 'data'
DATA_DIR.mkdir(exist_ok=True)


def save_to_json(apartments: List[Dict[str, Any]]) -> None:
    filename = f'apartments__{datetime.now().strftime("%Y%m%d%H%M%S")}.json'
    filepath = DATA_DIR / filename

    try:
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(apartments, file, ensure_ascii=False, indent=4)
        logging.info(f"Successfully saved {len(apartments)} apartments to {filepath}")

    except Exception as e:
        logging.error(f"Failed to save data to {filepath}: {e}")

def _combine_json_files() -> None:
    filename = f'combined_apartments__{datetime.now().strftime("%Y%m%d%H%M%S")}.json'
    output_filepath = DATA_DIR / filename

    # Combine
    json_files = glob.glob(os.path.join(DATA_DIR, "*.json"))
    combined_data = []
    for file_path in json_files:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            combined_data.extend(data)


    # Write
    with open(output_filepath, 'w', encoding='utf-8') as file:
        json.dump(combined_data, file, ensure_ascii=False, indent=4)


    # Remove
    files_removed = 0
    for file_path in json_files:
        if file_path != output_filepath:
            os.remove(file_path)
            files_removed += 1


if __name__ == "__main__":
    _combine_json_files()
