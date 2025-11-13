import os

from pathlib import Path

import config
from sampling import get_sample
from calling_github import clone, get_commits


def main():
    print("Hello from autumn-2025!")
    sample = get_sample()
    print(sample)
    for id in sample:
        commits = get_commits(full_name=id, path="README.md", since=config.SINCE, until=config.UNTIL)
        print(commits.totalCount)
        url = f"https://github.com/{id}.git"
        root = Path(__file__).resolve().parent.parent
        path = os.path.join(root, f"data/clones/{id}.git")
        if os.path.exists(path):
            print(f"Not cloning because the path already exists.")
        else:
            repo = clone(url=url, path=path, depth=1)


if __name__ == "__main__":
    main()
