import pygit2
from pathlib import Path
from typing import Optional

import config
from dataframe import dataframe
from domain_model import Subject
from export import export_subjects
from get_root import get_root
from get_sample_provided_by_ebert_et_al import get_sample_provided_by_ebert_et_al
from get_subjects_of_each_repo import get_subjects_of_each_repo
from get_version import get_version
from is_ccdc_event import is_ccdc_event
from read_subjects_csv import read_subjects_csv
from search_for_ccdc_events import search_for_ccdc_events


root = get_root()
version = get_version(root)


def pipeline(subjects_csv_path: Optional[Path] = None):
    if subjects_csv_path is None:
        repos_to_investigate = get_sample_provided_by_ebert_et_al(
            csv_path=root / "data" / "samples" / "ebert_et_al_2022" / "sample_100.csv",
            k=config.NUMBER_OF_REPOS_TO_INVESTIGATE,
            random_state=config.RANDOM_STATE,
        )
        subjects = get_subjects_of_each_repo(
            repos=repos_to_investigate,
            since=config.SINCE,
            until=config.UNTIL,
            paths_to_consider=config.PATHS_TO_CONSIDER,
            commits_per_repo=config.ONLY_CLASSIFY_THIS_MANY_COMMITS_PER_REPO,
            random_state=config.RANDOM_STATE,
        )
        if config.EXPORTS_SUBJECTS:
            export_subjects(subjects, root, version)
    else:
        subjects_csv_path = Path(subjects_csv_path)  # falls str o.ä. übergeben wurde
        if not subjects_csv_path.is_file():
            raise ValueError(
                f"subjects_csv_path must point to an existing CSV file, "
                f"but got: {subjects_csv_path}"
            )
        if subjects_csv_path.suffix.lower() != ".csv":
            raise ValueError(
                f"subjects_csv_path must be a .csv file, but got: {subjects_csv_path}"
            )
        subjects = read_subjects_csv(subjects_csv_path)
    _continue(subjects)


def _continue(subjects: set[Subject]):
    if config.IS_NAYSAYER:
        def _naysayer(subject: Subject, hunk: pygit2.DiffHunk) -> bool:
            return False
        classifier = _naysayer
    else:
        classifier = is_ccdc_event
    
    results = search_for_ccdc_events(
        subjects=subjects,
        channel_detector=_return_empty_set,
        classifier=classifier
    )
    print(dataframe(results))


def _return_empty_set(subject: Subject, hunk: pygit2.DiffHunk) -> set[str]:
    return set()