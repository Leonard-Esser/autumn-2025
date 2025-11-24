from pathlib import Path
from pygit2 import Repository, Commit, Diff
from typing import Iterable
import pandas as pd

from decorators import stop_the_clock
from diffing import flatten, get_changes, get_patch, get_diff
from io_helpers import export_changes
from model import Event, EventWhereCommunicationChannelDocumentationHasChanged


@stop_the_clock
def get_ccd_events_of_entire_repo(
    repo: Repository,
    full_name_of_repo: str,
    commits_dict: dict[str, Iterable[str]],
    classifier,
    version: str,
    path_to_changes_dir: str | Path
):
    frames = []
    for commit_sha in commits_dict:
        commit: Commit = repo.get(commit_sha)
        paths_to_consider: Iterabel[str] = commits_dict[commit_sha]
        frames.append(
            get_ccd_events_of_single_commit(
                full_name_of_repo,
                commit,
                paths_to_consider,
                classifier,
                version,
                path_to_changes_dir
            )
        )
    return pd.concat(frames, ignore_index=True)


def get_ccd_events_of_single_commit(
    full_name_of_repo: str,
    commit: Commit,
    paths: Iterable[str],
    classifier,
    version: str,
    path_to_changes_dir: str | Path
):
    rows = []
    for path in paths:
        flattened_changes = flatten(
            get_changes(
                get_patch(
                    get_diff(commit),
                    path
                )
            )            
        )
        export_changes(flattened_changes, commit.short_id, path_to_changes_dir)
        rows.extend(
            create_rows(
                classifier(
                    full_name_of_repo,
                    commit.id,
                    path,
                    flattened_changes
                ),
                version
            )
        )
    
    return pd.DataFrame(rows)


def create_rows(
    event: EventWhereCommunicationChannelDocumentationHasChanged | Event,
    version: str = None
) -> list[dict]:
    rows = []

    base = {}
    if version:
        base = {**base, "Version": version}
    
    base = {
        **base,
        "Repository": event.get_repo(),
        "Commit": event.get_commit(),
        "Path": event.get_path(),
    }

    if isinstance(event, EventWhereCommunicationChannelDocumentationHasChanged):
        if event.does_not_affect_any_specific_channel:
            rows.append({**base, "Affects CCD": 1})
            return rows

        for channel, changes in event.get_changes_per_channel().items():
            for type_of_change in changes:
                rows.append(
                    {
                        **base,
                        "Affects CCD": 1,
                        "Affected Channel": channel,
                        "Type of Change": type_of_change,
                    }
                )
        return rows
    
    if isinstance(event, Event):
        rows.append({**base, "Affects CCD": 0})

    return rows


def main():
    print(f"Hello from {Path(__file__).name}!")


if __name__ == "__main__":
    main()