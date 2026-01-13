import logging
import random
from collections import defaultdict
from collections.abc import Iterable
from datetime import datetime

import github
from github import GithubException, UnknownObjectException

logger = logging.getLogger(__name__)


def get_repo(gh: github.Github, full_name: str, lazy: bool = False):
    try:
        return gh.get_repo(full_name_or_id=full_name, lazy=lazy)
    except UnknownObjectException as exc:
        # 404: repository not found
        logger.error(f"[Error] Repository not found for '{full_name}': {exc.status} {exc.data}")
        return None
    except GithubException as exc:
        # Other GitHub API exceptions
        logger.error(f"[Error] GitHub API error for '{full_name}': {exc.status} {exc.data}")
        return None
    except Exception as exc:
        # Any other unexpected errors
        logger.error(f"[Error] Unexpected error while fetching '{full_name}': {exc}")
        return None


def get_commits_and_their_paths(
    repo: github.Repository,
    since: datetime | None,
    until: datetime | None,
    *,
    paths_to_consider: Iterable[str] | None = None,
    commits_per_repo: int | None = None,
    random_state: int | None = None,
) -> dict[github.Commit, list[str]]:
    commits_of_each_path = _for_each_file_get_commits(
        paths_to_consider,
        repo=repo,
        since=since,
        until=until,
    )
    commits_and_paths = _get_commits_and_their_paths(
        commits_of_each_path=commits_of_each_path,
        sort_result_right_away=False,
    )
    commits = list(commits_and_paths.keys())
    if commits_per_repo is not None and commits_per_repo > 0:
        k = min(commits_per_repo, len(commits))
        if random_state is not None:
            random.seed(random_state)
        commits = random.sample(commits, k)
        commits_and_paths = {commit: commits_and_paths[commit] for commit in commits}
    return commits_and_paths


def _for_each_path_get_commits(
    repo: github.Repository,
    paths_to_consider: Iterable[str],
    since: datetime | None,
    until: datetime | None,
) -> dict[str, list[github.Commit]]:
    result: dict[str, list[github.Commit]] = {}
    for path in paths_to_consider:
        if since is None and until is None:
            result[path] = repo.get_commits(
                path=path,
            )
            continue
        if since is None:
            result[path] = repo.get_commits(
                path=path,
                until=until,
            )
            continue
        if until is None:
            result[path] = repo.get_commits(
                path=path,
                since=since,
            )
            continue
        result[path] = repo.get_commits(
            path=path,
            since=since,
            until=until
        )
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


def name_check(
    full_name_of_repo: str,
    *,
    gh: github.Github,
    swallows_archived_repos: bool = False,
) -> str | None:
    repo = get_repo(gh=gh, full_name=full_name_of_repo, lazy=False)
    if repo is None or (swallows_archived_repos and repo.archived):
        return None
    return repo.full_name


def _for_each_file_get_commits(
    files: Iterable[str],
    *,
    repo: github.Repository,
    since: datetime| None,
    until: datetime| None,
) -> dict[str, list[github.Commit]]:
    result: dict[str, list[github.Commit]] = {}
    if since is None:
        since = github.GithubObject.NotSet
    if until is None:
        until = github.GithubObject.NotSet
    for file in files:
        commits = repo.get_commits(
            path=file,
            since=since,
            until=until
        )
        if not commits:
            logger.info((
                "Calling github.Repository.get_commits "
                f"with path={file}, since={since}, and until={until} "
                "returned no commits."
            ))
        result[file] = repo.get_commits(
            path=file,
            since=since,
            until=until
        )
    return result