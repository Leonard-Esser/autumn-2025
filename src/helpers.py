import subprocess

from pathlib import Path


def run_git_gc(working_dir: str):
    if not path_is_git_dir(working_dir):
        raise ValueError(f"{working_dir} is not a valid Git repository")
    
    return subprocess.run(
        args=["git", "gc", "--aggressive", "--prune=now"],
        cwd=working_dir,
        text=True,
        capture_output=True,
        check=False
    )


def path_is_git_dir(path: str):
    path = Path(path)
    return path.is_dir() and (path.name.endswith(".git") or (path / ".git").exists())