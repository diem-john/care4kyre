import json
import os
from pathlib import Path


def generate_master_json():
    master_db = {}
    root_dir = Path("data/raw")

    # Iterate through each category folder
    for category_dir in root_dir.iterdir():
        if category_dir.is_dir():
            category_name = category_dir.name.replace('_', ' ').title()
            json_dir = category_dir / "json_files"

            if json_dir.exists():
                master_db[category_name] = {}
                for json_file in json_dir.glob("*.json"):
                    part_name = json_file.stem.upper()
                    with open(json_file, 'r', encoding='utf-8') as f:
                        try:
                            master_db[category_name][part_name] = json.load(f)
                        except json.JSONDecodeError:
                            print(f"Error parsing {json_file}")

    # Save the result
    with open("data/question_bank.json", "w", encoding="utf-8") as f:
        json.dump(master_db, f, indent=2)
    print("Successfully generated data/question_bank.json!")


if __name__ == "__main__":
    generate_master_json()