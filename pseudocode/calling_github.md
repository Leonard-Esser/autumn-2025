```
from os import PathLike
import os

from datetime import datetime
from github import Github, Repository
from pathlib import Path
from pygit2 import clone_repository
from typing import Iterable

from decorators import stop_the_clock
from auth import get_remote_callbacks, get_github
import config


@stop_the_clock
def clone(
    url: str,
    path: str,
    bare: bool = True,
    depth: int = 0
):
    return clone_repository(
        url=url,
        path=path,
        bare=bare,
        callbacks=get_remote_callbacks(),
        depth=depth
    )


def get_repo(github: Github, full_name: str, lazy: bool = False):
    return github.get_repo(full_name_or_id=full_name, lazy=lazy)


@stop_the_clock
def get_commits_for_multiple_paths(
    repo: Repository,
    paths: Iterable[str],
    since: datetime,
    until: datetime
):
    commits = (
        commit
        for path in paths
        for commit in get_commits(repo, path, since, until)
    )
    unique = {commit.sha: commit for commit in commits}.values()
    return sorted(unique, key=lambda c: c.commit.committer.date, reverse=False)


@stop_the_clock
def get_commits_dict_for_multiple_paths(
    repo: Repository,
    paths: Iterable[str],
    since: datetime,
    until: datetime
) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    commit_date: dict[str, datetime] = {}

    for path in paths:
        commits = get_commits(repo, path, since, until)
        for commit in commits:
            sha = commit.sha

            if sha not in result:
                result[sha] = []
                commit_date[sha] = commit.commit.committer.date

            result[sha].append(path)

    for sha in result:
        result[sha] = sorted(result[sha])

    sorted_result = dict(
        sorted(
            result.items(),
            key=lambda item: commit_date[item[0]]
        )
    )

    return sorted_result


def get_commits(
    repo: Repository,
    path: str,
    since: datetime,
    until: datetime
):
    return repo.get_commits(
        path=path,
        since=since,
        until=until
    )


def main():
    print(f"Hello from {Path(__file__).name}!")


if __name__ == "__main__":
    main()
```
