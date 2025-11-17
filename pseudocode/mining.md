```
from pathlib import Path
from pygit2 import Repository, Commit, Diff
from typing import Iterable
import pandas as pd

from decorators import stop_the_clock


@stop_the_clock
def get_file_specific_commits(repo, full_name_of_repo, commits, path):
    rows = []
    for commit in commits:
        rows.append({
            "Repository": full_name_of_repo,
            "Commit": commit.sha,
            "Path": path
        })
    return pd.DataFrame(rows)


@stop_the_clock
def get_ccd_events_of_entire_repo(
    repo: Repository,
    commits_dict: dict[str, Iterable[str]],
    finder
):
    frames = []
    for commit_sha in commits_dict:
        commit: Commit = repo.get(commit_sha)
        paths_to_consider: Iterabel[str] = commits_dict[commit_sha]
        frames.append(
            get_ccd_events_of_single_commit(commit, paths_to_consider, finder)
        )
    return pd.concat(frames, ignore_index=True)


def get_ccd_events_of_single_commit(
    commit: Commit,
    paths: Iterable[str],
    finder
):
    if commit.parent_ids:
        diff = commit.tree.diff_to_tree(
            commit.parents[0].tree
        )
    else:
        diff = commit.tree.diff_to_tree()
    rows = []
    for path in paths:
        ccd_events = finder(diff, path)
        if ccd_events:
            for ccd_event in ccd_events:
                rows.append(create_row(commit, path, ccd_event))
        else:
            rows.append(create_row_for_commit_only(commit, path))
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