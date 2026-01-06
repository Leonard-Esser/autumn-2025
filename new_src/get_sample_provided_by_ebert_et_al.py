import csv
import random
from urllib.parse import urlparse

from pathlib import Path
from typing import Optional, Sequence


def get_sample_provided_by_ebert_et_al(
    csv_path: str | Path,
    k: Optional[int] = None,
    random_state: Optional[int] = None,
) -> list[str]:
    results = _read_full_names_from_sample_provided_by_ebert_et_al(csv_path)
    if not results:
        return []
    
    if k is not None and k > 0:
        if random_state is not None:
            random.seed(random_state)
        return random.sample(results, k)
    
    return results


def _read_full_names_from_sample_provided_by_ebert_et_al(
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