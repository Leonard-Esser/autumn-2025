from collections.abc import Callable
from pathlib import Path

import pygit2

import config
import subjects_config
from analyze import analyze
from data_access import get_results_dir
from dataframes import COLUMNS_FOR_MANUAL_VERIFICATION, commits_df, dataframe, merge, repos_df
from decorators import stop_the_clock
from domain_model import Subject
from draw_ccdc_events import draw_ccdc_events
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
    
    repos = repos_df(
        root,
        returns_cached_repos_if_any=config.RETURNS_CACHED_DATA_IF_ANY,
        updates_cache=config.UPDATES_CACHE,
    )
    
    commits = commits_df(
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

    positives = draw_ccdc_events(
        results=results,
        k=config.NUMBER_OF_POSITIVE_EVENTS_TO_DRAW,
        random_state=config.RANDOM_STATE,
    )

    negatives = draw_ccdc_events(
        results=results,
        k=config.NUMBER_OF_NEGATIVE_EVENTS_TO_DRAW,
        logical_negation=True,
        random_state=config.RANDOM_STATE,
    )

    sample = subjects_config.normalized_script_hash()
    results_dir = get_results_dir(
        root,
        program_version=program_version,
        sample=sample,
    )

    results_df = merge(
        results=dataframe(results),
        commits=commits,
        repos=repos,
    )

    positives_df = merge(
        results=dataframe(positives),
        commits=commits,
    )

    negatives_df = merge(
        results=dataframe(negatives),
        commits=commits,
    )
    
    file_name = f"results_{program_version}_{sample}.csv"
    export_df(
        results_df,
        file_name,
        results_dir,
    )

    file_name = f"results_{program_version}_{sample}_focused.csv"
    export_df(
        results_df[COLUMNS_FOR_MANUAL_VERIFICATION],
        file_name,
        results_dir,
    )
    
    file_name = f"results_{program_version}_{sample}_positives.csv"
    export_df(
        positives_df[COLUMNS_FOR_MANUAL_VERIFICATION],
        file_name,
        results_dir,
    )
    
    file_name = f"results_{program_version}_{sample}_negatives.csv"
    export_df(
        negatives_df[COLUMNS_FOR_MANUAL_VERIFICATION],
        file_name,
        results_dir,
    )