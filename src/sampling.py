import csv
from pathlib import Path
from urllib.parse import urlparse

from decorators import delete_sooner_or_later


def read_full_names_from_sample_provided_by_ebert_et_al(
    csv_path: str | Path
) -> list[str]:
    results = []
    
    with Path(csv_path).open("r", encoding="utf-8", newline="") as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)  # skip the header
        
        for row in reader:
            if not row:
                continue
            
            repo_has_retired = row[-1].strip().lower() == "retired"
            if repo_has_retired:
                continue
            
            def extract_full_name():
                # assuming a URL like this one for example: https://github.com/leonard-esser/autumn-2025
                url = row[1]
                parsed = urlparse(url)
                parts = parsed.path.strip("/").split("/")
                if len(parts) >= 2:
                    full_name = f"{parts[-2]}/{parts[-1]}"
                    results.append(full_name)
            
            extract_full_name()
    
    return results


def main():
    print(f"Hello from {Path(__file__).name}!")


if __name__ == "__main__":
    main()