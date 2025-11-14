import pandas as pd
from pathlib import Path

from decorators import timer


@timer
def get_file_specific_commits(repo, full_name_of_repo, commits, path):
    rows = []
    for commit in commits:
        rows.append({
            "Repository": full_name_of_repo,
            "Commit": commit.sha,
            "Path": path
        })
    return pd.DataFrame(rows)


def main():
    print(f"Hello from {Path(__file__).name}!")


if __name__ == "__main__":
    main()