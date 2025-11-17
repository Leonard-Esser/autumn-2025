import csv
import os

from pathlib import Path
from pygit2 import Repository
from typing import Iterable

from helpers import get_latest_commit
from sampling import get_sample
import config


def get_path_to_destination_dir(
    root: str,
    name: str,
    repo_owner: str | None = None,
    repo_name: str | None = None,
    version: str | None = None
) -> str:
    parts = [root]
    parts.extend(config.PARTS_OF_BASE_OUTPUT_DIR)
    if version:
        parts.append(version)
    if repo_owner:
        parts.append(repo_owner)
    if repo_name:
        parts.append(repo_name)
    parts.append(name)
    return os.path.join(*parts)


def get_destination_of_samples(root: str, version: str | None = None) -> str:
    return get_path_to_destination_dir(root, config.NAME_OF_SAMPLES_DIR, version=version)


def get_destination_of_results(root: str, version: str | None = None) -> str:
    return get_path_to_destination_dir(root, config.NAME_OF_RESULTS_DIR, version=version)


def get_destination_of_commits(
    root: str,
    repo_owner: str,
    repo_name: str,
    version: str | None = None
) -> str:
    return get_path_to_destination_dir(
        root,
        config.NAME_OF_COMMITS_DIR,
        repo_owner,
        repo_name,
        version
    )


def get_destination_of_frames(
    root: str,
    repo_owner: str,
    repo_name: str,
    version: str | None = None
) -> str:
    return get_path_to_destination_dir(
        root,
        config.NAME_OF_FRAMES_DIR,
        repo_owner,
        repo_name,
        version
    )


def export_one_column_of_strings(
    export_goods: Iterable[str],
    file_name: str,
    destination: str
):
    file_ending = ".csv"
    if not file_name.lower().endswith(file_ending):
        file_name = file_name + file_ending
    path = os.path.join(destination, file_name)
    Path(destination).mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as csv_file:
        for export_good in export_goods:
            get_csv_writer(csv_file).writerow([export_good])


def get_csv_writer(csv_file):
    return csv.writer(csv_file)


def main():
    print(f"Hello from {Path(__file__).name}!")


if __name__ == "__main__":
    main()