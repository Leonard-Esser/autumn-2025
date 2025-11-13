import os

from pathlib import Path

from helpers import run_git_gc
from sampling import get_sample
from calling_github import clone, get_commits
import config


def main():
    sample = get_sample()
    for full_name in sample:
        commits = get_commits(
            full_name=full_name,
            path="README.md",
            since=config.SINCE,
            until=config.UNTIL
        )
        url = f"https://github.com/{full_name}.git"
        root = Path(__file__).resolve().parent.parent
        path = os.path.join(root, f"data/clones/{full_name}.git")
        if os.path.exists(path):
            print(f"Not cloning because the path already exists.")
        else:
            repo = clone(url=url, path=path)
            result = run_git_gc(working_dir=path)
            print(f"Running git gc {'was successful' if result.returncode == 0 else 'failed'}.")


if __name__ == "__main__":
    main()
