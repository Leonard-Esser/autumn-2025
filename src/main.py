import os
import time

from pathlib import Path
from pygit2 import Repository
import pandas as pd

from decorators import timer
from sampling import get_sample
from helpers import *
from calling_github import clone, get_commits
from mining import get_ccd_events_of_entire_repo, find_ccd_events
import config


@timer
def main():
    file_to_be_studied = config.FILE_TO_BE_STUDIED
    sample = get_sample()
    data = []
    for full_name in sample:
        commits = get_commits(
            full_name,
            file_to_be_studied,
            config.SINCE,
            config.UNTIL
        )
        url = get_url(full_name)
        root = Path(__file__).resolve().parent.parent
        bare_clones_dir = make_directory_for_bare_clones(root)
        path = create_path_for_git_directory(parent_dir=bare_clones_dir, full_name_of_repo=full_name)
        if path.exists():
            print(f"Not cloning because the path already exists.")
        else:
            clone(url=url, path=path)
            result = run_git_gc(working_dir=path)
            print(f"Running git gc {'was successful' if result.returncode == 0 else 'failed'}.")
        repo = Repository(path)
        commits = convert_to_pygit2_commits(commits, repo)
        df = get_ccd_events_of_entire_repo(
            repo,
            full_name,
            file_to_be_studied,
            commits,
            find_ccd_events
        )
        data.append(df)
        if config.DELETE_GIT_DIR_IMMEDIATELY:
            delete_git_dir(path)
    data = pd.concat(data, ignore_index=True)
    print(data)


if __name__ == "__main__":
    main()