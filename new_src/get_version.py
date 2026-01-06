import pygit2
from pathlib import Path


def get_version(root: Path):
    this_repo = pygit2.Repository(root)
    return _get_latest_commit(this_repo).short_id


def _get_latest_commit(repo: pygit2.Repository):
    return repo.revparse_single('HEAD')