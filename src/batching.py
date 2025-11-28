from pathlib import Path
from pygit2 import Repository
from typing import Iterable
import pandas as pd

from calling_github import get_github, get_repo, for_each_path_get_commits, get_commits_and_their_paths, clone
from data_frames_care import create_df_for_repo, create_df_for_commits
from helpers import get_url, make_directory_for_bare_clones, create_path_for_git_directory, delete_git_dir
from io_helpers import get_output_dir, export_commits, export_df
from mining import get_ccd_events_of_entire_repo
import config


def process_each_sample(
    sample: Iterable[str],
    root: Path,
    version: str,
    classifier
) -> pd.DataFrame:
    
    github = get_github()
    
    ccd_events_of_all_repos = []
    repos_df = []
    
    for sampled_repo in sample:
        full_name = sampled_repo
        owner, name = full_name.split("/")
        
        repo = get_repo(github, full_name)
        repo_df = create_df_for_repo(repo)
        repos_df.append(repo_df)
        
        commits_of_each_path = for_each_path_get_commits(
            repo,
            config.PATHS_TO_CONSIDER,
            config.SINCE,
            config.UNTIL
        )
        commits_and_their_paths = get_commits_and_their_paths(
            commits_of_each_path,
            sort_result_right_away=True
        )
        commits_df = create_df_for_commits(commits_and_their_paths.keys())
        commits_and_their_paths = {
            commit.sha: paths for commit, paths in commits_and_their_paths.items()
        }
        export_commits(
            commits_and_their_paths,
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
            print(f"Not cloning because the path already exists")
        else:
            clone(url=url, path=path)
            result = run_git_gc(working_dir=path)
            print(f"Running git gc {'was successful' if result.returncode == 0 else 'failed'}")
        repo = Repository(path)
        
        ccd_events = get_ccd_events_of_entire_repo(
            repo,
            full_name,
            commits_and_their_paths,
            classifier,
            version,
            get_output_dir(root, config.NAME_OF_CHANGES_DIR, owner, name, version)
        )
        ccd_events = repo_df.merge(
            ccd_events,
            left_on="Repository Full Name",
            right_on="Repository",
            how="left"
        ).drop(columns=["Repository"])
        ccd_events = commits_df.merge(
            ccd_events,
            left_on="Commit SHA",
            right_on="Commit",
            how="left"
        )
        export_df(
            ccd_events,
            "ccd events",
            get_output_dir(root, config.NAME_OF_FRAMES_DIR, owner, name, version)
        )
        ccd_events_of_all_repos.append(ccd_events)

        if config.DELETE_GIT_DIR_IMMEDIATELY:
            delete_git_dir(path)
    
    repos_df = pd.concat(repos_df, ignore_index=True)
    export_df(
        repos_df,
        "repos",
        get_output_dir(root, config.NAME_OF_FRAMES_DIR, version=version)
    )
    
    return pd.concat(ccd_events_of_all_repos, ignore_index=True)