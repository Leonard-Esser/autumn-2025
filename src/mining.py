import logging
import random
from collections.abc import Callable

from pathlib import Path
from pygit2 import Repository, Commit, Diff
from typing import Iterable
import pandas as pd

import config
from decorators import stop_the_clock
from diffing import flatten, get_changes, get_patch, get_diff
from io_helpers import export_changes
from model import CCDCEvent, Event, EventKey


logger = logging.getLogger(__name__)


@stop_the_clock
def get_ccd_events_of_entire_repo(
    repo: Repository,
    full_name_of_repo: str,
    commits_dict: dict[str, Iterable[str]],
    classifier_pipeline: Callable[[Commit, EventKey], CCDCEvent | Event],
    version: str,
    path_to_changes_dir: str | Path
):
    frames = []
    k = config.ONLY_CLASSIFY_THIS_MANY_COMMITS_PER_REPO
    if k > 0:
        if config.RANDOM_STATE:
            random.seed(config.RANDOM_STATE)
        commit_shas = list(commits_dict.keys())
        if len(commit_shas) > k:
            sampled_shas = set(random.sample(commit_shas, k))
            commits_dict = {sha: commits_dict[sha] for sha in sampled_shas}
    for commit_sha in commits_dict:
        commit: Commit = repo.get(commit_sha)
        paths_to_consider: Iterabel[str] = commits_dict[commit_sha]
        frames.append(
            get_ccd_events_of_single_commit(
                full_name_of_repo,
                commit,
                paths_to_consider,
                classifier_pipeline,
                version,
                path_to_changes_dir
            )
        )
    return pd.concat(frames, ignore_index=True)


@stop_the_clock
def get_ccd_events_of_single_commit(
    full_name_of_repo: str,
    commit: Commit,
    paths: Iterable[str],
    classifier_pipeline: Callable[[Commit, EventKey], CCDCEvent | Event],
    version: str | None = None,
    path_to_changes_dir: str | Path | None = None
):
    rows = []
    for path in paths:
        flattened_changes = flatten(
            get_changes(
                get_patch(
                    get_diff(commit, config.CONTEXT_LINES),
                    path
                )
            )
        )
        if not config.DO_NOT_EXPORT_CHANGES and path_to_changes_dir:
            export_changes(flattened_changes, commit.short_id + f"-{path}", path_to_changes_dir)
        rows.extend(
            create_rows(
                classifier_pipeline(
                    commit,
                    EventKey(
                        full_name_of_repo,
                        commit.id,
                        path
                    )
                ),
                version
            )
        )
    
    return pd.DataFrame(rows)


def create_rows(
    event: CCDCEvent | Event,
    version: str = None
) -> list[dict]:
    rows = []

    base = {}
    if version:
        base = {**base, "Version": version}
    
    base = {
        **base,
        "Repository": event.get_key.get_full_name_of_repo,
        "Commit": event.get_key.get_commit_sha,
        "Path": event.get_key.get_path,
    }

    if isinstance(event, CCDCEvent):
        if event.get_types_of_change:
            for type_of_change in event.get_types_of_change:
                rows.append(
                    {
                        **base,
                        "Affects CCD": 1,
                        "Type of Change": type_of_change,
                    }
                )
        else:
            rows.append(
                {
                    **base,
                    "Affects CCD": 1,
                    "Type of Change": 0,
                }
            )
        return rows
    
    if isinstance(event, Event):
        rows.append(
            {
                **base,
                "Affects CCD": 0,
                "Type of Change": 0,
            }
        )

    return rows


def main():
    print(f"Hello from {Path(__file__).name}!")


if __name__ == "__main__":
    main()