from os import PathLike
import os

from datetime import datetime
from github import Repository
from pathlib import Path
from pygit2 import clone_repository

from decorators import timer
from auth import get_github, get_remote_callbacks
from sampling import get_sample
import config


@timer
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


@timer
def get_commits(
    full_name: str,
    path: str,
    since: datetime,
    until: datetime,
    lazy: bool = False,
):
    github = get_github()
    repo = github.get_repo(full_name_or_id=full_name, lazy=lazy)
    return repo.get_commits(
        path=path,
        since=since,
        until=until
    )


def main():
    print(f"Hello from {Path(__file__).name}!")


if __name__ == "__main__":
    main()