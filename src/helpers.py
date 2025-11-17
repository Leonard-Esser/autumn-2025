from shutil import rmtree
import os
import subprocess

from github import PaginatedList
from pathlib import Path
from pygit2 import Repository

from decorators import timer


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


@timer
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


def convert_to_pygit2_commits(
    pygithub_commits: PaginatedList,
    repo: Repository
):
    return [
        repo.get(commit.sha)
        for commit in pygithub_commits
    ]


def get_latest_commit(repo: Repository):
    return repo.revparse_single('HEAD')


def main():
    print(f"Hello from {Path(__file__).name}!")


if __name__ == "__main__":
    main()