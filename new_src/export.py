from __future__ import annotations

import csv
from collections.abc import Iterable

from pathlib import Path

import config
from domain_model import Subject


def export_subjects(subjects: Iterable[Subject], root: Path, version: str) -> Path:
    output_dir = _get_output_dir(root, config.SUBJECTS_DIR, version=version)
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "subjects.csv"
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


def _get_output_dir(
    root: Path,
    name: str,
    *,
    repo_owner: str | None = None,
    repo_name: str | None = None,
    version: str | None = None,
) -> Path:
    path = root
    for part in config.PARTS_OF_BASE_OUTPUT_DIR:
        path /= part
    if version:
        path /= version
    path /= name
    if repo_owner:
        path /= repo_owner
    if repo_name:
        path /= repo_name
    return path