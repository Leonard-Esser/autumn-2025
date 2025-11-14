from pathlib import Path
from pygit2 import Repository, Commit, Diff
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
def get_ccd_events(repo: Repository, full_name_of_repo, commits, path, classify_func):
    rows = [
        classify_func(repo, full_name_of_repo, commit, path)
        for commit in commits
    ]
    return pd.DataFrame(rows)


def classify(repo: Repository, full_name_of_repo, commit: Commit, path):
    if len(commit.parent_ids) == 0:
        pass
    diff = repo.diff(commit.id, commit.parent_ids[0])
    return {
        "Repository": full_name_of_repo,
        "Commit": commit.id,
        "Time": commit.commit_time,
        "Path": path,
        "Diff": diff.patchid,
    }


def main():
    print(f"Hello from {Path(__file__).name}!")


if __name__ == "__main__":
    main()