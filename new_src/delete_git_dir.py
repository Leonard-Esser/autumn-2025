import os
from pathlib import Path
from shutil import rmtree

from helpers import raise_error_if_path_is_not_git_dir


def delete_git_dir(path: Path):
    raise_error_if_path_is_not_git_dir(path)
    repo_owner_dir = path.parent
    rmtree(path)
    if _dir_is_empty(repo_owner_dir):
        repo_owner_dir.rmdir()


def _dir_is_empty(path: Path):
    return len(os.listdir(path)) == 0