from collections.abc import Iterable
from datetime import datetime
from pathlib import Path

import pandas as pd
from export import export_df, get_output_dir

import config
from auth import get_github
from calling_github import get_commits_and_their_paths, get_repo


def commits_df(
    *,
    returns_cached_commits_if_any: bool,
    updates_cache: bool,
    root: Path,
    repos: Iterable[str],
    commits_since: datetime,
    commits_until: datetime,
    files: Iterable[str],
    k_commits_per_repo: int | None = None,
    version: str | None = None,
    random_state: int | None = None,
) -> pd.DataFrame:
    cache = get_output_dir(
        root,
        version=version,
        config_sha=config.normalized_script_hash(),
    )
    if returns_cached_commits_if_any:
        commits_csv = cache / config.COMMITS_CSV
        if commits_csv.exists():
            return pd.read_csv(commits_csv)
    
    gh = get_github()
    rows: list[dict[str, object]] = []
    for full_name_of_repo in repos:
        repo = get_repo(gh, full_name_of_repo)
        if repo is None:
            continue
        commits_and_their_paths = get_commits_and_their_paths(
                repo,
                commits_since,
                commits_until,
                paths_to_consider=files,
                commits_per_repo=k_commits_per_repo,
                random_state=random_state
            )
        for commit in commits_and_their_paths.keys():
            rows.append(
                {
                    "full_name_of_repo": full_name_of_repo,
                    "sha": commit.sha,
                    "url": commit.html_url,
                    "message": commit.commit.message,
                    "date": commit.commit.committer.date,
                }
            )
    df = pd.DataFrame(
        rows,
        columns=[
            "full_name_of_repo",
            "sha",
            "url",
            "message",
            "date",
        ],
    )
    if not df.empty:
        df = df.sort_values(
            ["full_name_of_repo", "date", "sha"],
            kind="stable",
            ignore_index=True,
        )
    if updates_cache:
        export_df(
            df,
            config.COMMITS_CSV,
            cache
        )
    return df