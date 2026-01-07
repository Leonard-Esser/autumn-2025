from collections.abc import Iterable

from datetime import datetime
from pathlib import Path

from domain_model import Subject
from export import export_subjects, get_output_dir
from read_subjects_csv import read_subjects_csv
from get_sample_provided_by_ebert_et_al import get_sample_provided_by_ebert_et_al
from get_subjects_of_each_repo import get_subjects_of_each_repo
import config


def draw_subjects(
    *,
    returns_cached_subjects_if_any: bool,
    updates_cache: bool,
    root: Path,
    commits_since: datetime,
    commits_until: datetime,
    files: Iterable[str],
    k_commits_per_repo: int | None = None,
    k_repos: int | None = None,
    version: str | None = None,
    random_state: int | None = None,
) -> set[Subject]:
    cache = get_output_dir(
        root,
        version=version,
        config_sha=config.normalized_script_hash(),
    )
    if returns_cached_subjects_if_any:
        subjects_csv = cache / config.SUBJECTS_CSV
        if subjects_csv.exists():
            return read_subjects_csv(subjects_csv)
    
    repos_to_investigate = get_sample_provided_by_ebert_et_al(
        root=root,
        excludes_retired_repos=False,
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