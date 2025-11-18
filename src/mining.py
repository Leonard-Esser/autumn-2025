from pathlib import Path
from pygit2 import Repository, Commit, Diff
from typing import Iterable
import pandas as pd

from decorators import stop_the_clock
from diffing import flatten, get_patch
from io_helpers import export_changes


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
    finder,
    path_to_changes_dir: str | Path
):
    frames = []
    for commit_sha in commits_dict:
        commit: Commit = repo.get(commit_sha)
        paths_to_consider: Iterabel[str] = commits_dict[commit_sha]
        frames.append(
            get_ccd_events_of_single_commit(
                commit,
                paths_to_consider,
                finder,
                path_to_changes_dir
            )
        )
    return pd.concat(frames, ignore_index=True)


def get_ccd_events_of_single_commit(
    commit: Commit,
    paths: Iterable[str],
    finder,
    path_to_changes_dir: str | Path
):
    if commit.parent_ids:
        diff = commit.tree.diff_to_tree(
            commit.parents[0].tree
        )
    else:
        diff = commit.tree.diff_to_tree()
    rows = []
    for path in paths:
        rows.append(
            create_row(
                commit,
                path,
                finder(diff, path, commit, path_to_changes_dir)
            )
        )
    return pd.DataFrame(rows)


def find_ccd_events(diff: Diff, path: str):
    pass


def is_ccd_event(
    diff: Diff,
    path: str,
    commit: Commit,
    path_to_changes_dir: str | Path
) -> bool:
    changes = flatten(get_patch(diff, path))
    export_changes(changes, commit.short_id, path_to_changes_dir)
    return False


def create_row(commit: Commit, path: str, is_ccd_event: bool):
    return {
        "Commit SHA": commit.id,
        "Path": path,
        "CCD Event": 1 if is_ccd_event else 0,
    }


def main():
    print(f"Hello from {Path(__file__).name}!")


if __name__ == "__main__":
    main()