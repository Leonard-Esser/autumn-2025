import csv
import random
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path

import config
import subjects_config
from domain_model import Subject
from export import export_subjects, get_output_dir
from get_subjects_of_each_repo import get_subjects_of_each_repo
from sample_provided_by_ebert_et_al import draw_repos


def draw_subjects(
    *,
    returns_cached_subjects_if_any: bool,
    updates_cache: bool,
    root: Path,
    repos: Iterable[str],
    commits_since: datetime | None,
    commits_until: datetime | None,
    files: Iterable[str],
    excludes_retired_repos: bool,
    k_commits_per_repo: int | None = None,
    k_repos: int | None = None,
    version: str | None = None,
    random_state: int | None = None,
) -> set[Subject]:
    cache = get_output_dir(
        root,
        version=version,
        extra_dir=f"config_{subjects_config.normalized_script_hash()}",
    )
    if returns_cached_subjects_if_any:
        subjects_csv = cache / config.SUBJECTS_CSV
        if subjects_csv.exists():
            return draw_subjects_from_csv(subjects_csv)
    
    repos_to_investigate = draw_repos(
        k=k_repos,
        random_state=random_state,
    )
    subjects = get_subjects_of_each_repo(
        repos=repos_to_investigate,
        since=commits_since,
        until=commits_until,
        paths_to_consider=files,
        commits_per_repo=k_commits_per_repo,
        random_state=random_state
    )
    if updates_cache:
        export_subjects(
            subjects,
            config.SUBJECTS_CSV,
            cache
        )
    return subjects


def draw_subjects_from_csv(
    path: Path,
    *,
    k: int | None = None,
    random_state: int | None = None,
) -> set[Subject]:
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
    if k is not None and k > 0 and k < len(subjects):
        if random_state is not None:
            random.seed(random_state)
        subjects = random.sample(subjects, k)
    return subjects