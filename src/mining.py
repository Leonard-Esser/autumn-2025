from pathlib import Path
import pandas as pd

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


@timer
def get_ccd_events(repo, full_name_of_repo, commits, path, classify_func):
    rows = [
        classify_func(repo, full_name_of_repo, commit, path)
        for commit in commits
    ]
    return pd.DataFrame(rows)


def classify(repo, full_name_of_repo, commit, path):
    return {
        "Repository": full_name_of_repo,
        "Commit": commit.sha,
        "Path": path
    }


def main():
    print(f"Hello from {Path(__file__).name}!")


if __name__ == "__main__":
    main()