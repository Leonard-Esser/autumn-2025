from pathlib import Path


def raise_error_if_path_is_not_git_dir(path: Path):
    if not _path_is_git_dir(path):
        raise ValueError(f"{path} is not a valid Git repository")


def _path_is_git_dir(path: Path):
    return path.suffix == ".git"