from collections.abc import Iterable
from datetime import datetime
from pathlib import Path

import pandas as pd

import subjects_config
from auth import get_github
from calling_github import get_commits_and_their_paths, get_repo
from data_access import get_cache_dir
from domain_model import Result
from export import export_df
from sample_provided_by_ebert_et_al import draw_repos

COLUMNS_FOR_MANUAL_VERIFICATION: list[str] = [
    "url",
    "path",
    "is_ccdc_event",
    "detected_channel",
]


def repos_df(
    root: Path,
    *,
    returns_cached_repos_if_any: bool,
    updates_cache: bool,
) -> pd.DataFrame:
    cache = get_cache_dir(
        root,
    )
    file_name = "all_repos.csv"
    if returns_cached_repos_if_any:
        repos_csv = cache / file_name
        if repos_csv.exists():
            return pd.read_csv(repos_csv)
    
    gh = get_github()
    rows: list[dict[str, object]] = []
    for full_name_of_repo in draw_repos():
        repo = get_repo(gh, full_name_of_repo)
        if repo is None:
            continue
        rows.append(
            {
                # identity
                "id": repo.id,
                "full_name": repo.full_name,
                
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
            "full_name",
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
        df = df.sort_values("full_name", kind="stable", ignore_index=True)
    
    if updates_cache:
        export_df(
            df,
            file_name,
            cache,
        )
    
    return df


def commits_df(
    root: Path,
    *,
    returns_cached_commits_if_any: bool,
    updates_cache: bool,
    repos: Iterable[str],
    k_repos: int | None = None,
    commits_since: datetime | None,
    commits_until: datetime | None,
    files: Iterable[str],
    k_commits_per_repo: int | None = None,
    random_state: int | None = None,
) -> pd.DataFrame:
    sample = subjects_config.normalized_script_hash()
    cache = get_cache_dir(
        root,
        sample=sample,
    )
    file_name = f"commits_{sample}.csv"
    if returns_cached_commits_if_any:
        path = cache / file_name
        if path.exists():
            return pd.read_csv(path)
    
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
            random_state=random_state,
        )
        for commit in commits_and_their_paths.keys():
            rows.append(
                {
                    "full_name_of_repo": full_name_of_repo,
                    "sha": commit.sha,
                    "url": f"{commit.html_url} ",
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
            file_name,
            cache,
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


def merge(
    *,
    results: pd.DataFrame,
    commits: pd.DataFrame,
    repos: pd.DataFrame | None,
) -> pd.DataFrame:
    if repos is not None:
        results = results.merge(
            repos,
            left_on="full_name_of_repo",
            right_on="full_name",
            how="left",
        )
        results.drop(columns=["full_name"])
    results = results.merge(
        commits,
        left_on=["full_name_of_repo", "commit_sha"],
        right_on=["full_name_of_repo", "sha"],
        how="left",
    )
    results.drop(columns=["sha"])
    return results