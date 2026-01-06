from collections.abc import Iterable

from datetime import datetime
from typing import Optional

import github


def get_repo(github: github.Github, full_name: str, lazy: bool = False):
    try:
        return github.get_repo(full_name_or_id=full_name, lazy=lazy)
    except UnknownObjectException as exc:
        # 404: repository not found
        get_logger(__name__).error(f"[Error] Repository not found for '{full_name}': {exc.status} {exc.data}")
        return None
    except GithubException as exc:
        # Other GitHub API exceptions
        get_logger(__name__).error(f"[Error] GitHub API error for '{full_name}': {exc.status} {exc.data}")
        return None
    except Exception as exc:
        # Any other unexpected errors
        get_logger(__name__).error(f"[Error] Unexpected error while fetching '{full_name}': {exc}")
        return None


def get_commits(
    repo: github.Repository,
    since: datetime,
    until: datetime,
    path: Optional[str] = None
):
    if path is not None:
        return repo.get_commits(
            since=since,
            until=until
        )
    
    return repo.get_commits(
        path=path,
        since=since,
        until=until
    )