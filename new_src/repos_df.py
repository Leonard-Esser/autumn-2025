from collections.abc import Iterable
from pathlib import Path

import pandas as pd
from export import export_df, get_output_dir
from get_sample_provided_by_ebert_et_al import get_sample_provided_by_ebert_et_al

import config
from auth import get_github
from calling_github import get_repo


def repos_df(
    *,
    returns_cached_repos_if_any: bool,
    updates_cache: bool,
    root: Path
) -> pd.DataFrame:
    output_dir = get_output_dir(root)
    if returns_cached_repos_if_any:
        repos_csv = output_dir / config.REPOS_CSV
        if repos_csv.exists():
            return pd.read_csv(repos_csv)
    
    repos_to_investigate = get_sample_provided_by_ebert_et_al(
        root=root,
        excludes_retired_repos=False,
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