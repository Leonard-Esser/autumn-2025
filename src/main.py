import os

from pathlib import Path
import pandas as pd

from helpers import get_url, make_directory_for_bare_clones, create_path_for_git_directory, run_git_gc, get_new_df, delete_git_dir
from sampling import get_sample
from calling_github import clone, get_commits
import config


def main():
    sample = get_sample()
    data = []
    for full_name in sample:
        commits = get_commits(
            full_name,
            config.FILE_TO_BE_STUDIED,
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
            repo = clone(url=url, path=path)
            result = run_git_gc(working_dir=path)
            print(f"Running git gc {'was successful' if result.returncode == 0 else 'failed'}.")
        df = get_new_df(config.COLUMNS, full_name)
        data.append(df)
        delete_git_dir(path)
    data = pd.concat(data)
    print(data)


if __name__ == "__main__":
    main()