from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime

import pandas as pd

from auth import get_github
from calling_github import get_commits, get_repo


def commits_df(
    repos: Iterable[str],
    since: datetime,
    until: datetime
) -> pd.DataFrame:
    gh = get_github()
    rows: list[dict[str, object]] = []
    for full_name_of_repo in repos:
        repo = get_repo(gh, full_name_of_repo)
        commits = get_commits(repo, since=since, until=until)
        for commit in commits:
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
    return df