import pygit2
from pathlib import Path

import config
from dataframe import dataframe
from domain_model import Subject
from get_root import get_root
from get_sample_provided_by_ebert_et_al import get_sample_provided_by_ebert_et_al
from get_subjects_of_each_repo import get_subjects_of_each_repo
from is_ccdc_event import is_ccdc_event
from search_for_ccdc_events import search_for_ccdc_events
from setup_logging import setup_logging


def main():
    root = get_root()
    setup_logging(root)

    repos = get_sample_provided_by_ebert_et_al(
        csv_path=Path(root) / "data" / "samples" / "ebert_et_al_2022" / "sample_100.csv",
        k=config.NUMBER_OF_REPOS_TO_INVESTIGATE,
        random_state=config.RANDOM_STATE
    )

    subjects = get_subjects_of_each_repo(
        repos=repos,
        since=config.SINCE,
        until=config.UNTIL,
        paths_to_consider=config.PATHS_TO_CONSIDER,
        commits_per_repo=config.ONLY_CLASSIFY_THIS_MANY_COMMITS_PER_REPO,
        random_state=config.RANDOM_STATE
    )

    results = search_for_ccdc_events(
        subjects=subjects,
        channel_detector=return_empty_set,
        classifier=is_ccdc_event
    )

    print(dataframe(results))


def return_empty_set(subject: Subject, hunk: pygit2.DiffHunk) -> set[str]:
    return set()


def naysayer(subject: Subject, hunk: pygit2.DiffHunk) -> bool:
    return False


if __name__ == "__main__":
    main()