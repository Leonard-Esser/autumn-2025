from pathlib import Path
from pygit2 import Repository
from typing import Iterable
import pandas as pd

from calling_github import get_github, get_repo, get_commits_dict_for_multiple_paths, clone
from helpers import get_url, make_directory_for_bare_clones, create_path_for_git_directory, delete_git_dir
from io_helpers import get_output_dir, export_commits, export_df
from mining import get_ccd_events_of_entire_repo
import config


def process_each_sample(
    sample: Iterable[str],
    root: Path,
    version: str,
    finder
) -> pd.DataFrame:
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
            get_output_dir(root, config.NAME_OF_COMMITS_DIR, owner, name, version)
        )

        url = get_url(full_name)
        bare_clones_dir = make_directory_for_bare_clones(root)
        path = create_path_for_git_directory(
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
            finder,
            get_output_dir(root, config.NAME_OF_CHANGES_DIR, owner, name, version)
        ).assign(Repository=full_name)
        export_df(
            df,
            "ccd_events",
            get_output_dir(root, config.NAME_OF_FRAMES_DIR, owner, name, version)
        )
        data.append(df)
        if config.DELETE_GIT_DIR_IMMEDIATELY:
            delete_git_dir(path)
    
    return pd.concat(data, ignore_index=True)