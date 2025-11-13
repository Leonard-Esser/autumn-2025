from os import PathLike
import os

from datetime import datetime
from github import Repository
from pathlib import Path
from pygit2 import clone_repository


import config
from auth import get_github, get_remote_callbacks
from sampling import get_sample


def clone(
    url: str,
    path: str | PathLike[str],
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
    sample = get_sample()
    for full_name in sample:
        commits = get_commits(full_name=full_name, path="README.md", since=config.SINCE, until=config.UNTIL)
        print(commits.totalCount)
        for commit in commits:
            print(commit.sha)
        url = f"https://github.com/{full_name}.git"
        root = Path(__file__).resolve().parent.parent
        path = os.path.join(root, f"data/clones/{full_name}.git")
        if os.path.exists(path):
            print(f"Not cloning because the path already exists.")
        else:
            repo = clone(url=url, path=path, depth=1)


if __name__ == "__main__":
    main()