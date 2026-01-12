import csv
from collections.abc import Iterable
from pathlib import Path

import pandas as pd

from domain_model import Subject


def export_subjects(
    subjects: Iterable[Subject],
    file_name: str,
    destination: str | Path,
) -> Path:
    destination = _create_path_and_make_dir(destination)
    csv_path = destination / _ensure_correct_file_ending(file_name, ".csv")
    # Deduplicate by full triple, then sort:
    # full_name_of_repo ASC, commit_sha ASC (grouped by sorting), path ASC
    unique_subjects = sorted(
        {(s.full_name_of_repo, s.commit_sha, s.path) for s in subjects},
        key=lambda t: (t[0], t[1], t[2]),
    )
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(["full_name_of_repo", "commit_sha", "path"])
        writer.writerows(unique_subjects)
    return csv_path


def _create_path_and_make_dir(path: str | Path):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _ensure_correct_file_ending(file_name: str, file_ending: str) -> str:
    if not file_name.endswith(file_ending):
        file_name = file_name + file_ending
    return file_name


def export_df(
    df: pd.DataFrame,
    file_name: str,
    destination: str | Path,
    index: bool = False,
) -> Path:
    destination = _create_path_and_make_dir(destination)
    csv_path = destination / _ensure_correct_file_ending(file_name, ".csv")
    df.to_csv(csv_path, index=index)
    return csv_path


def export_set_of_names(
    names: Iterable[str],
    *,
    csv_path: Path | str,
    col_name: str,
) -> Path:
    csv_path = Path(csv_path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    unique_names = sorted(
        {(name,) for name in names}
    )
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow([col_name])
        writer.writerows(unique_names)
    return csv_path