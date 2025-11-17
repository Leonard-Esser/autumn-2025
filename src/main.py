import os
import time

from pathlib import Path
from pygit2 import Repository
import pandas as pd

from calling_github import get_github, get_repo, get_commits_dict_for_multiple_paths, clone
from decorators import timer
from io_helpers import export_one_column_of_strings, get_output_dir, export_commits
from mining import get_ccd_events_of_entire_repo, find_ccd_events
from sampling import get_sample
import config
import helpers


@timer
def main():
    root = Path(__file__).resolve().parent.parent
    this_repo = Repository(root)
    version = helpers.get_latest_commit(this_repo).short_id
    
    sample = get_sample()
    export_one_column_of_strings(
        sample,
        "sample",
        get_output_dir(root, "samples", version=version)
    )
    
    data = []
    for full_name in sample:
        github = get_github()
        repo = get_repo(github, full_name)
        commits_dict = get_commits_dict_for_multiple_paths(
            repo,
            config.PATHS_TO_CONSIDER,
            config.SINCE,
            config.UNTIL
        )
        owner, name = full_name.split("/")
        export_commits(
            commits_dict,
            "commits.json",
            get_output_dir(root, "commits", owner, name, version)
        )

        url = helpers.get_url(full_name)
        bare_clones_dir = helpers.make_directory_for_bare_clones(root)
        path = helpers.create_path_for_git_directory(
            parent_dir=bare_clones_dir,
            full_name_of_repo=full_name
        )
        if path.exists():
            print(f"Not cloning because the path already exists.")
        else:
            clone(url=url, path=path)
            result = run_git_gc(working_dir=path)
            print(f"Running git gc {'was successful' if result.returncode == 0 else 'failed'}.")
        repo = Repository(path)
        df = get_ccd_events_of_entire_repo(
            repo,
            commits_dict,
            find_ccd_events
        ).assign(Repository=full_name)
        data.append(df)
        if config.DELETE_GIT_DIR_IMMEDIATELY:
            helpers.delete_git_dir(path)
    data = pd.concat(data, ignore_index=True)
    print(data)


if __name__ == "__main__":
    main()