from collections.abc import Callable, Iterable
from datetime import datetime
from pathlib import Path

import pandas as pd
import pygit2

import config
import subjects_config
from auth import get_github
from calling_github import get_commits_and_their_paths, get_repo
from domain_model import Result, Subject
from export import export_df, get_output_dir
from get_sample_provided_by_ebert_et_al import get_sample_provided_by_ebert_et_al
from search_for_ccdc_events import search_for_ccdc_events


def repos_df(
    *,
    returns_cached_repos_if_any: bool,
    updates_cache: bool,
    root: Path,
    excludes_retired_repos: bool,
) -> pd.DataFrame:
    output_dir = get_output_dir(root)
    if returns_cached_repos_if_any:
        repos_csv = output_dir / config.REPOS_CSV
        if repos_csv.exists():
            return pd.read_csv(repos_csv)
    
    repos_to_investigate = get_sample_provided_by_ebert_et_al(
        root=root,
        excludes_retired_repos=excludes_retired_repos,
    )
    gh = get_github()
    rows: list[dict[str, object]] = []
    for full_name_of_repo in repos_to_investigate:
        repo = get_repo(gh, full_name_of_repo)
        if repo is None:
            continue
        rows.append(
            {
                # identity
                "id": repo.id,
                "full_name_of_repo": repo.full_name,
                
                # urls
                "homepage": repo.homepage,
                "clone_url": repo.clone_url,
                "git_url": repo.git_url,
                "teams_url": repo.teams_url,
                
                # time
                "created_at": repo.created_at,
                "pushed_at": repo.pushed_at,
                "updated_at": repo.updated_at,
                
                # features
                "has_discussions": repo.has_discussions,
                "has_issues": repo.has_issues,
                "has_pages": repo.has_pages,
                "has_projects": repo.has_projects,
                "has_wiki": repo.has_wiki,
                
                # counts
                "forks_count": repo.forks_count,
                "open_issues_count": repo.open_issues_count,
                "stargazers_count": repo.stargazers_count,
                "subscribers_count": repo.subscribers_count,
                "size": repo.size,
            }
        )
    df = pd.DataFrame(
        rows,
        columns=[
            "id",
            "full_name_of_repo",
            "homepage",
            "clone_url",
            "git_url",
            "teams_url",
            "created_at",
            "pushed_at",
            "updated_at",
            "has_discussions",
            "has_issues",
            "has_pages",
            "has_projects",
            "has_wiki",
            "forks_count",
            "open_issues_count",
            "stargazers_count",
            "subscribers_count",
            "size",
        ],
    )
    if not df.empty:
        df = df.sort_values("full_name_of_repo", kind="stable", ignore_index=True)
    if updates_cache:
        export_df(
            df,
            config.REPOS_CSV,
            output_dir
        )
    return df


def commits_df(
    *,
    returns_cached_commits_if_any: bool,
    updates_cache: bool,
    root: Path,
    repos: Iterable[str],
    commits_since: datetime | None,
    commits_until: datetime | None,
    files: Iterable[str],
    k_commits_per_repo: int | None = None,
    version: str | None = None,
    random_state: int | None = None,
) -> pd.DataFrame:
    cache = get_output_dir(
        root,
        version=version,
        extra_dir=f"config_{subjects_config.normalized_script_hash()}",
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


def dataframe(result_set: Iterable[Result]) -> pd.DataFrame:
    """
    Returns a DataFrame with:
      - one row per channel in Result.detected_channels
      - if detected_channels is empty: exactly one row with detected_channel=None
      - one column per field of Result
      - Subject expanded into its three fields
      - stable column order and explicit dtypes
    """
    rows: list[dict[str, object]] = []
    for result in result_set:
        base = {
            "full_name_of_repo": result.subject.full_name_of_repo,
            "commit_sha": result.subject.commit_sha,
            "path": result.subject.path,
            "is_ccdc_event": result.is_ccdc_event,
        }
        if result.detected_channels:
            for channel in result.detected_channels:
                rows.append({**base, "detected_channel": channel})
        else:
            rows.append({**base, "detected_channel": None})
    columns = [
        "full_name_of_repo",
        "commit_sha",
        "path",
        "is_ccdc_event",
        "detected_channel",
    ]
    df = pd.DataFrame.from_records(rows, columns=columns)
    df = df.astype(
        {
            "full_name_of_repo": "string",
            "commit_sha": "string",
            "path": "string",
            "is_ccdc_event": "bool",
            "detected_channel": "string",
        }
    )
    return df