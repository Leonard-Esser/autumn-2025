import csv
import random
from urllib.parse import urlparse

from pathlib import Path
from typing import Optional, Sequence


def get_sample_provided_by_ebert_et_al(
    *,
    root: Path,
    excludes_retired_repos: bool,
    k: int | None = None,
    random_state: int | None = None,
) -> list[str]:
    results: list[str] = []
    csv_path = root / "data" / "samples" / "ebert_et_al_2022" / "sample_100.csv"
    with csv_path.open("r", encoding="utf-8", newline="") as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)  # skip the header
        
        for row in reader:
            if not row:
                continue            
            repo_has_retired = row[-1].strip().lower() == "retired"
            if excludes_retired_repos and repo_has_retired:
                continue
            # assuming a URL like this one for example: https://github.com/leonard-esser/autumn-2025
            url = row[1]
            parsed = urlparse(url)
            parts = parsed.path.strip("/").split("/")
            if len(parts) >= 2:
                full_name = f"{parts[-2]}/{parts[-1]}"
                results.append(full_name)
    if not results:
        return []
    
    if k is not None and k > 0:
        k = min(k, len(results))
        if random_state is not None:
            random.seed(random_state)
        return random.sample(results, k)
    
    return results