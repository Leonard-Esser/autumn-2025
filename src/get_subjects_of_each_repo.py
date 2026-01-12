import logging
from collections.abc import Iterable
from datetime import datetime

from auth import get_github
from calling_github import get_commits_and_their_paths, get_repo
from domain_model import Subject

logger = logging.getLogger(__name__)


def get_subjects_of_each_repo(
    repos: Iterable[str],
    since: datetime | None,
    until: datetime | None,
    paths_to_consider: Iterable[str],
    commits_per_repo: int | None = None,
    random_state: int | None = None,
) -> set[Subject]:
    """
    For each repo, collects commits touching any of the given paths within [since, until],
    then returns a set of Subject(repo, commit_sha, path).

    If commits_per_repo is set, we randomly sample that many *commits* per repo
    (without replacement). For sampled commits, we include all paths (from
    paths_to_consider) that the commit touched.
    """
    gh = get_github()
    all_subjects: set[Subject] = set()
    for full_name_of_repo in repos:
        repo = get_repo(gh, full_name_of_repo, lazy=False)
        if repo is None:
            continue
        try:
            commits_and_paths = get_commits_and_their_paths(
                repo,
                since,
                until,
                paths_to_consider=paths_to_consider,
                commits_per_repo=commits_per_repo,
                random_state=random_state
            )
            for commit in commits_and_paths.keys():
                for path in commits_and_paths.get(commit, []):
                    all_subjects.add(
                        Subject(
                            full_name_of_repo=full_name_of_repo,
                            commit_sha=commit.sha,
                            path=path,
                        )
                    )
        except Exception as exc:
            logger.error(f"[Error] Unexpected error while processing '{full_name_of_repo}': {exc}")
    return all_subjects