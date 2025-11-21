from pathlib import Path
from pygit2 import Repository, Commit, Diff
from typing import Iterable
import pandas as pd

from decorators import stop_the_clock
from diffing import flatten, get_patch, get_diff
from io_helpers import export_changes


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
    rows = []
    for path in paths:
        changes = flatten(
            get_patch(
                get_diff(commit),
                path
            )
        )
        export_changes(changes, commit.short_id, path_to_changes_dir)
        rows.append(
            create_row(
                commit,
                path,
                finder(changes)
            )
        )
    return pd.DataFrame(rows)


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