```
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
def get_ccd_events_of_entire_repo(repo: Repository, full_name_of_repo: str, path: str, commits, finder):
    frames = [
        get_ccd_events_of_single_commit(commit, path, finder)
        for commit in commits
    ]
    return pd.concat(frames, ignore_index=True).assign(Repository=full_name_of_repo)


def get_ccd_events_of_single_commit(commit: Commit, path: str, finder):
    if commit.parent_ids:
        diff = commit.tree.diff_to_tree(
            commit.parents[0].tree
        )
    else:
        diff = commit.tree.diff_to_tree()
    ccd_events = finder(diff, path)
    if ccd_events:
        rows = [
            create_row(commit, path, ccd_event)
            for ccd_event in ccd_events
        ]
    else:
        rows = [
            create_row_for_commit_only(commit, path)
        ]
    return pd.DataFrame(rows)


def find_ccd_events(diff: Diff, path: str):
    pass


def create_row_(commit: Commit, path: str, ccd_event):
    pass


def create_row_for_commit_only(commit: Commit, path: str):
    return {
        "Commit SHA": commit.id,
        "Path": path,
        "CCD Event": 0,
    }


def main():
    print(f"Hello from {Path(__file__).name}!")


if __name__ == "__main__":
    main()
```