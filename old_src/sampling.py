import csv
import pandas as pd
import random
from pathlib import Path
from typing import Sequence
from urllib.parse import urlparse

from decorators import delete_sooner_or_later


def get_sample_provided_by_ebert_et_al(
    csv_path: str | Path,
    k: int,
    random_state: int | None = None,
) -> list[str]:
    results = _read_full_names_from_sample_provided_by_ebert_et_al(csv_path)
    if not results:
        return []
    
    if k > 0:
        if random_state:
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


def draw_k_random_distinct_rows_from_sample(
    base_sample: pd.DataFrame,
    columns: Sequence[str],
    k: int = 100,
    export_path: str | Path | None = None,
    random_state: int | None = None,
) -> pd.DataFrame:
    """
    Draw k random distinct rows (without replacement) from base_sample.

    Distinctness is defined based on the combination of the columns provided
    in `columns`. The returned DataFrame contains only these columns.
    Optionally exports the result as a CSV file if `export_path` is provided.

    Parameters
    ----------
    base_sample : pd.DataFrame
        The input DataFrame (the sampling population).
    columns : Sequence[str]
        Column names that define uniqueness and are returned in the result.
    k : int, optional
        Number of rows to sample (default: 100).
    export_path : str | Path | None, optional
        File path for CSV export. If None, no export is performed.
    random_state : int | None, optional
        Seed for reproducibility.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing k randomly selected distinct rows.
    """
    if k <= 0:
        raise ValueError("k must be greater than 0.")

    # Verify that all requested columns exist in the DataFrame
    missing_cols = set(columns) - set(base_sample.columns)
    if missing_cols:
        raise KeyError(f"The following columns are missing in base_sample: {missing_cols}")

    # Remove duplicates based on the selected columns
    unique_df = base_sample.drop_duplicates(subset=list(columns))

    # Ensure that enough distinct rows exist
    if len(unique_df) < k:
        raise ValueError(
            f"Only {len(unique_df)} distinct rows exist for columns {columns}, "
            f"but k={k} was requested (sampling without replacement is not possible)."
        )

    # Random sampling without replacement
    sampled = unique_df.sample(
        n=k,
        replace=False,
        random_state=random_state,
    )

    # Keep only the requested columns
    result = sampled.loc[:, list(columns)]

    # Optional CSV export
    if export_path is not None:
        export_path = Path(export_path)
        export_path.parent.mkdir(parents=True, exist_ok=True)
        result.to_csv(export_path, index=False)

    return result


def main():
    print(f"Hello from {Path(__file__).name}!")


if __name__ == "__main__":
    main()