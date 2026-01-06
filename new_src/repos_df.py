from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

import config
from auth import get_github
from calling_github import get_repo
from export import export_df, get_output_dir
from get_root import get_root
from get_sample_provided_by_ebert_et_al import get_sample_provided_by_ebert_et_al
from setup_logging import setup_logging


def repos_df(full_names: Iterable[str]) -> pd.DataFrame:
    gh = get_github()
    rows: list[dict[str, object]] = []
    for full_name in full_names:
        repo = get_repo(gh, full_name)
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
    return df


def main():
    root = get_root()
    setup_logging(root)
    repos = get_sample_provided_by_ebert_et_al(
        csv_path=root / "data" / "samples" / "ebert_et_al_2022" / "sample_100.csv"
    )
    df = repos_df(repos)
    destination = get_output_dir(
        root,
        config.REPOS_DIR
    )
    export_df(
        df,
        "repos.csv",
        destination
    )


if __name__ == "__main__":
    main()