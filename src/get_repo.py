import subprocess
from pathlib import Path

import pygit2

from auth import get_remote_callbacks
from get_logger import get_logger
from helpers import raise_error_if_path_is_not_git_dir


def get_repo(
    *,
    full_name_of_repo: str,
    root: Path,
) -> pygit2.Repository:
    path = _get_path(full_name_of_repo, root)
    if path.exists():
        return pygit2.Repository(path)
    repo = _bare_clone(
        url=_get_url(full_name_of_repo),
        path=path
    )
    result = _run_git_gc(working_dir=path)
    get_logger(__name__).info(
        f"Running git gc {'was successful' if result.returncode == 0 else 'failed'}"
    )
    return repo


def _get_path(full_name_of_repo: str, root: Path) -> Path:
    return _create_path_for_git_directory(
        full_name_of_repo=full_name_of_repo,
        parent_dir=_make_directory_for_bare_clones(root)
    )


def _create_path_for_git_directory(
    full_name_of_repo: str,
    parent_dir: Path
):
    path = Path(parent_dir, f"{full_name_of_repo}.git")
    raise_error_if_path_is_not_git_dir(path)
    return path


def _make_directory_for_bare_clones(
    parent_dir: Path,
    parents: bool = True,
    exist_ok: bool = True
):
    bare_clones_dir = Path(parent_dir, "data/bare_clones")
    bare_clones_dir.mkdir(parents=parents, exist_ok=exist_ok)
    return bare_clones_dir


def _bare_clone(
    url: str,
    path: str,
    depth: int = 0
) -> pygit2.Repository:
    return pygit2.clone_repository(
        url=url,
        path=path,
        bare=True,
        callbacks=get_remote_callbacks(),
        depth=depth
    )


def _get_url(full_name_of_repo: str) -> str:
    return f"https://github.com/{full_name_of_repo}.git"


def _run_git_gc(working_dir: Path):
    raise_error_if_path_is_not_git_dir(working_dir)
    return subprocess.run(
        args=["git", "gc", "--aggressive", "--prune=now"],
        cwd=working_dir,
        text=True,
        capture_output=True,
        check=False
    )