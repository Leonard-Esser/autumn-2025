import pygit2
from pathlib import Path

import pandas as pd

import config
from commits_df import commits_df
from dataframe import dataframe
from domain_model import Subject
from export import export_df, export_subjects, get_cache_dir, get_output_dir
from get_root import get_root
from get_sample_provided_by_ebert_et_al import get_sample_provided_by_ebert_et_al
from get_subjects_of_each_repo import get_subjects_of_each_repo
from get_version import get_version
from is_ccdc_event import is_ccdc_event
from read_subjects_csv import read_subjects_csv
from repos_df import repos_df
from search_for_ccdc_events import search_for_ccdc_events


root = get_root()
version = get_version(root)


def pipeline():
    subjects: set[Subject] | None = None
    if not config.IGNORES_CACHE:
        subjects_csv = _get_cache_dir() / config.SUBJECTS_CSV
        if subjects_csv.exists():
            subjects = read_subjects_csv(subjects_csv)
    if not subjects:
        repos_to_investigate = get_sample_provided_by_ebert_et_al(
            csv_path=root / "data" / "samples" / "ebert_et_al_2022" / "sample_100.csv",
            k=config.NUMBER_OF_REPOS_TO_INVESTIGATE,
            random_state=config.RANDOM_STATE
        )
        subjects = get_subjects_of_each_repo(
            repos=repos_to_investigate,
            since=config.SINCE,
            until=config.UNTIL,
            paths_to_consider=config.PATHS_TO_CONSIDER,
            commits_per_repo=config.ONLY_CLASSIFY_THIS_MANY_COMMITS_PER_REPO,
            random_state=config.RANDOM_STATE
        )
        if not config.IGNORES_CACHE:
            export_subjects(
                subjects,
                config.SUBJECTS_CSV,
                _get_cache_dir()
            )
    
    repos_csv = get_output_dir(root) / config.REPOS_CSV
    if repos_csv.exists():
        repos = pd.read_csv(repos_csv)
    else:
        repos_to_investigate = get_sample_provided_by_ebert_et_al(
            csv_path=root / "data" / "samples" / "ebert_et_al_2022" / "sample_100.csv"
        )
        repos = repos_df(repos_to_investigate)
        export_df(repos, config.REPOS_CSV, get_output_dir(root))
    
    commits_csv = get_output_dir(root) / config.COMMITS_CSV
    if commits_csv.exists():
        commits = pd.read_csv(commits_csv)
    else:
        commits = commits_df(
            repos={s.full_name_of_repo for s in subjects},
            since=config.SINCE,
            until=config.UNTIL,
            paths_to_consider=config.PATHS_TO_CONSIDER,
            commits_per_repo=config.ONLY_CLASSIFY_THIS_MANY_COMMITS_PER_REPO,
            random_state=config.RANDOM_STATE
        )
        export_df(commits, config.COMMITS_CSV, get_output_dir(root))
    
    _continue(subjects)


def _get_cache_dir():
    return get_cache_dir(
        root,
        config.normalized_script_hash(),
        version=version
    )


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