import csv
from pathlib import Path

from domain_model import Subject


def read_subjects_csv(path: Path) -> set[Subject]:
    subjects: set[Subject] = set()
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            subjects.add(
                Subject(
                    full_name_of_repo=row["full_name_of_repo"],
                    commit_sha=row["commit_sha"],
                    path=row["path"],
                )
            )
    return subjects