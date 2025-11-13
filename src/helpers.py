from shutil import rmtree
import os
import subprocess

from pathlib import Path


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


def main():
    root = Path(__file__).resolve().parent.parent
    bare_clones_dir = make_directory_for_bare_clones(root)
    path = create_path_for_git_directory(parent_dir=bare_clones_dir, full_name_of_repo="leonardesser/autumn-2025")
    path.mkdir(parents=True, exist_ok=True)
    another_path = create_path_for_git_directory(parent_dir=bare_clones_dir, full_name_of_repo="leonardesser/winter-2025")
    another_path.mkdir(parents=True, exist_ok=True)
    delete_git_dir(path)
    delete_git_dir(another_path)


if __name__ == "__main__":
    main()