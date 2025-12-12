import csv
import json
import os

from pathlib import Path
from pygit2 import Repository
from typing import Iterable
import pandas as pd

import config


def export_sample(
    sample: Iterable[int] | Iterable[str],
    root: str,
    version: str
):
    export_one_column_of_strings(
        sample,
        "sample",
        get_output_dir(root, config.NAME_OF_SAMPLES_DIR, version=version)
    )


def export_one_column_of_strings(
    export_goods: Iterable[str],
    file_name: str,
    destination: str | Path
):
    destination = create_path_and_make_dir(destination)
    path = destination / ensure_correct_file_ending(file_name, ".csv")
    with open(path, "w", newline="", encoding="utf-8") as csv_file:
        for export_good in export_goods:
            get_csv_writer(csv_file).writerow([export_good])


def get_output_dir(
    root: str,
    name: str,
    repo_owner: str | None = None,
    repo_name: str | None = None,
    version: str | None = None
) -> Path:
    parts = [root]
    parts.extend(config.PARTS_OF_BASE_OUTPUT_DIR)
    if version:
        parts.append(version)
    parts.append(name)
    if repo_owner:
        parts.append(repo_owner)
    if repo_name:
        parts.append(repo_name)
    return Path(*parts)


def create_path_and_make_dir(path: str | Path):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def ensure_correct_file_ending(file_name: str, file_ending: str) -> str:
    if not file_name.endswith(file_ending):
        file_name = file_name + file_ending
    return file_name


def get_csv_writer(csv_file):
    return csv.writer(csv_file)


def export_commits(
    commits_dict: dict[str, list[str]],
    file_name: str,
    destination: str | Path
) -> None:
    destination = create_path_and_make_dir(destination)
    ensure_correct_file_ending(file_name, ".json")
    file_path = destination / file_name
    with file_path.open("w", encoding="utf-8") as f:
        json.dump(commits_dict, f, indent=2, ensure_ascii=False)


def export_ccd_events(
    data: pd.DataFrame,
    file_name: str,
    root: Path,
    version: str
):
    export_df(
        data,
        file_name,
        get_output_dir(root, config.NAME_OF_FRAMES_DIR, version=version)
    )


def export_df(
    df: pd.DataFrame,
    file_name: str,
    destination: str | Path,
    index: bool = False
) -> None:
    destination = create_path_and_make_dir(destination)
    path = destination / ensure_correct_file_ending(file_name, ".csv")
    df.to_csv(path, index=index)


def export_changes(
    changes: str,
    file_name: str,
    destination: str | Path
):
    destination = create_path_and_make_dir(destination)
    path = destination / ensure_correct_file_ending(file_name, ".txt")
    with path.open("w", encoding="utf-8") as f:
        f.write(changes)


def export_test_result(
    events_df: pd.DataFrame,
    summary: str | None,
    separator: str | None,
    file_name: str,
    destination: str | Path,
    index: bool = False,
    index_label: str | None = None,
) -> None:
    destination = create_path_and_make_dir(destination)
    path = destination / ensure_correct_file_ending(file_name, ".csv")
    
    events_df.to_csv(path, index=index, index_label=index_label)
    
    if summary:
        with open(path, "a", newline="", encoding="utf-8") as csv_file:
            writer = get_csv_writer(csv_file)
            writer.writerow([separator])
            writer.writerow([summary])


def main():
    print(f"Hello from {Path(__file__).name}!")


if __name__ == "__main__":
    main()