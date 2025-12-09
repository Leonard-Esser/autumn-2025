from shutil import rmtree
import os
import subprocess

import pygit2
from github import PaginatedList
from pathlib import Path

from calling_github import clone
from decorators import stop_the_clock


def get_version(root: Path):
    this_repo = pygit2.Repository(root)
    return get_latest_commit(this_repo).short_id


def get_latest_commit(repo: pygit2.Repository):
    return repo.revparse_single('HEAD')


def get_url(full_name: str):
    return f"https://github.com/{full_name}.git"


def make_directory_for_bare_clones(
    parent_dir: Path,
    parents: bool = True,
    exist_ok: bool = True
):
    bare_clones_dir = Path(parent_dir, "data/bare_clones")
    bare_clones_dir.mkdir(parents=parents, exist_ok=exist_ok)
    return bare_clones_dir


def create_path_for_git_directory(
    parent_dir: Path,
    full_name_of_repo: str
):
    path = Path(parent_dir, f"{full_name_of_repo}.git")
    raise_error_if_path_is_not_git_dir(path)
    return path


def raise_error_if_path_is_not_git_dir(path: Path):
    if not path_is_git_dir(path):
        raise ValueError(f"{path} is not a valid Git repository")


def path_is_git_dir(path: Path):
    return path.suffix == ".git"


@stop_the_clock
def run_git_gc(working_dir: Path):
    raise_error_if_path_is_not_git_dir(working_dir)
    return subprocess.run(
        args=["git", "gc", "--aggressive", "--prune=now"],
        cwd=working_dir,
        text=True,
        capture_output=True,
        check=False
    )


def delete_git_dir(path: Path):
    raise_error_if_path_is_not_git_dir(path)
    repo_owner_dir = path.parent
    rmtree(path)
    if dir_is_empty(repo_owner_dir):
        repo_owner_dir.rmdir()


def dir_is_empty(path: Path):
    return len(os.listdir(path)) == 0


def clone_if_necessary(
    root: Path,
    full_name_of_repo: str,
    silent: bool = True
) -> pygit2.Repository:
    url = get_url(full_name_of_repo)
    bare_clones_dir = make_directory_for_bare_clones(root)
    path = create_path_for_git_directory(
        parent_dir=bare_clones_dir,
        full_name_of_repo=full_name_of_repo
    )
    if path.exists():
        if not silent:
            print(f"Not cloning because the path already exists")
    else:
        clone(url=url, path=path)
        result = run_git_gc(working_dir=path)
        if not silent:
            print(f"Running git gc {'was successful' if result.returncode == 0 else 'failed'}")
    return pygit2.Repository(path)


def main():
    print(f"Hello from {Path(__file__).name}!")


if __name__ == "__main__":
    main()