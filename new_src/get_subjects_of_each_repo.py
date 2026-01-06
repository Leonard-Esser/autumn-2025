import random
from collections import defaultdict
from collections.abc import Iterable

from datetime import datetime
from typing import Optional

import github
from github.GithubException import GithubException, UnknownObjectException

from auth import get_github
from calling_github import get_commits, get_repo
from domain_model import Subject
from get_logger import get_logger


def get_subjects_of_each_repo(
    repos: Iterable[str],
    since: datetime,
    until: datetime,
    paths_to_consider: Iterable[str],
    commits_per_repo: Optional[int] = None,
    random_state: int | None = None
) -> set[Subject]:
    """
    For each repo, collects commits touching any of the given paths within [since, until],
    then returns a set of Subject(repo, commit_sha, path).

    If commits_per_repo is set, we randomly sample that many *commits* per repo
    (without replacement). For sampled commits, we include all paths (from
    paths_to_consider) that the commit touched.
    """
    log = get_logger(__name__)
    gh = get_github()
    all_subjects: set[Subject] = set()
    for full_name_of_repo in repos:
        repo = get_repo(gh, full_name_of_repo, lazy=False)
        if repo is None:
            continue
        try:
            commits_of_each_path = _for_each_path_get_commits(
                repo=repo,
                paths_to_consider=paths_to_consider,
                since=since,
                until=until,
            )
            commits_and_paths = _get_commits_and_their_paths(
                commits_of_each_path=commits_of_each_path,
                sort_result_right_away=False,
            )
            if not commits_and_paths:
                continue
            commits = list(commits_and_paths.keys())
            if commits_per_repo is not None and commits_per_repo > 0:
                k = min(commits_per_repo, len(commits))
                if random_state is not None:
                    random.seed(random_state)
                commits = random.sample(commits, k)
            for commit in commits:
                for path in commits_and_paths.get(commit, []):
                    all_subjects.add(
                        Subject(
                            full_name_of_repo=full_name_of_repo,
                            commit_sha=commit.sha,
                            path=path,
                        )
                    )
        except Exception as exc:
            log.error(f"[Error] Unexpected error while processing '{full_name_of_repo}': {exc}")
    return all_subjects


def _for_each_path_get_commits(
    repo: github.Repository,
    paths_to_consider: Iterable[str],
    since: datetime,
    until: datetime,
) -> dict[str, list[github.Commit]]:
    result: dict[str, list[github.Commit]] = {}
    for path in paths_to_consider:
        result[path] = get_commits(repo, since, until, path)
    return result


def _get_commits_and_their_paths(
    commits_of_each_path: dict[str, list[github.Commit]],
    sort_result_right_away: bool = False
) -> dict[github.Commit, list[str]]:
    result = defaultdict(list)
    for path, commits in commits_of_each_path.items():
        for commit in commits:
            result[commit].append(path)
    if not sort_result_right_away:
        return dict(result)
    for commit in result:
        result[commit].sort()
    sorted_items = sorted(
        result.items(),
        key=lambda item: item[0].commit.committer.date,
        reverse=True
    )
    return dict(sorted_items)