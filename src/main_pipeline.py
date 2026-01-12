from collections.abc import Callable
from pathlib import Path

import pygit2

import config
import subjects_config
from analyze import analyze
from data_access import get_results_dir
from dataframes import commits_df, dataframe, repos_df
from decorators import stop_the_clock
from domain_model import Subject
from draw_subjects import draw_subjects
from export import export_df


@stop_the_clock
def pipeline(
    root: Path,
    *,
    channel_detector: Callable[[Subject, pygit2.DiffHunk], set[str]],
    classifier: Callable[[Subject, pygit2.DiffHunk], bool],
    logs_progress: bool,
    deletes_git_dir_immediately: bool,
    program_version: str,
):
    subjects = draw_subjects(
        root,
        returns_cached_subjects_if_any=config.RETURNS_CACHED_DATA_IF_ANY,
        updates_cache=config.UPDATES_CACHE,
        k_repos=subjects_config.NUMBER_OF_REPOS_TO_INVESTIGATE,
        commits_since=subjects_config.COMMITS_SINCE,
        commits_until=subjects_config.COMMITS_UNTIL,
        files=subjects_config.FILES_TO_INVESTIGATE,
        k_commits_per_repo=subjects_config.ONLY_CLASSIFY_THIS_MANY_COMMITS_PER_REPO,
        random_state=subjects_config.RANDOM_STATE,
    )
    
    repos_df(
        root,
        returns_cached_repos_if_any=config.RETURNS_CACHED_DATA_IF_ANY,
        updates_cache=config.UPDATES_CACHE,
    )
    
    commits_df(
        root,
        returns_cached_commits_if_any=config.RETURNS_CACHED_DATA_IF_ANY,
        updates_cache=config.UPDATES_CACHE,
        repos={s.full_name_of_repo for s in subjects},
        commits_since=subjects_config.COMMITS_SINCE,
        commits_until=subjects_config.COMMITS_UNTIL,
        files=subjects_config.FILES_TO_INVESTIGATE,
        k_commits_per_repo=subjects_config.ONLY_CLASSIFY_THIS_MANY_COMMITS_PER_REPO,
        random_state=subjects_config.RANDOM_STATE,
    )
    
    results = analyze(
        subjects,
        root=root,
        channel_detector=channel_detector,
        classifier=classifier,
        logs_progress=logs_progress,
        deletes_git_dir_immediately=deletes_git_dir_immediately,
    )
    results_df = dataframe(results)
    sample = subjects_config.normalized_script_hash()
    export_df(
        results_df,
        f"results_{program_version}_{sample}.csv",
        get_results_dir(
            root,
            program_version=program_version,
            sample=sample,
        )
    )