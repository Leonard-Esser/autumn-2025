from collections import defaultdict
from os import PathLike
import os

from datetime import datetime
from github import Commit, Github, Repository
from pathlib import Path
from pygit2 import clone_repository
from typing import Iterable

from data_frames_care import create_df_for_commit
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


def for_each_path_get_commits(
    repo: Repository,
    paths: Iterable[str],
    since: datetime,
    until: datetime
) -> dict[str, list[Commit]]:
    result = {}
    for path in paths:
        result[path] = get_commits(repo, path, since, until)
    
    return result


def get_commits_and_their_paths(
    commits_of_each_path: dict[str, list[Commit]],
    sort_result_right_away: bool = False
) -> dict[Commit, list[str]]:

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