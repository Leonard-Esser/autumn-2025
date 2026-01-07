import pygit2
from commits_df import commits_df
from dataframe import dataframe
from domain_model import Subject
from draw_subjects import draw_subjects
from export import export_df, get_output_dir
from get_root import get_root
from get_version import get_version
from is_ccdc_event import is_ccdc_event
from repos_df import repos_df
from search_for_ccdc_events import search_for_ccdc_events

import config
from decorators import stop_the_clock

root = get_root()
version = get_version(root)

@stop_the_clock
def pipeline():
    subjects = draw_subjects(
        returns_cached_subjects_if_any=config.RETURNS_CACHED_DATA_IF_ANY,
        updates_cache=config.UPDATES_CACHE,
        root=root,
        commits_since=config.SINCE,
        commits_until=config.UNTIL,
        files=config.PATHS_TO_CONSIDER,
        k_commits_per_repo=config.ONLY_CLASSIFY_THIS_MANY_COMMITS_PER_REPO,
        k_repos=config.NUMBER_OF_REPOS_TO_INVESTIGATE,
        version=version,
        random_state=config.RANDOM_STATE,
    )
    
    repos_df(
        returns_cached_repos_if_any=config.RETURNS_CACHED_DATA_IF_ANY,
        updates_cache=config.UPDATES_CACHE,
        root=root,
    )
    
    commits_df(
        returns_cached_commits_if_any=config.RETURNS_CACHED_DATA_IF_ANY,
        updates_cache=config.UPDATES_CACHE,
        root=root,
        repos={s.full_name_of_repo for s in subjects},
        commits_since=config.SINCE,
        commits_until=config.UNTIL,
        files=config.PATHS_TO_CONSIDER,
        k_commits_per_repo=config.ONLY_CLASSIFY_THIS_MANY_COMMITS_PER_REPO,
        version=version,
        random_state=config.RANDOM_STATE,
    )
    
    if config.IS_NAYSAYER:
        def _naysayer(subject: Subject, hunk: pygit2.DiffHunk) -> bool:
            return False
        classifier = _naysayer
    else:
        classifier = is_ccdc_event
    
    results = search_for_ccdc_events(
        subjects=subjects,
        channel_detector=_return_empty_set,
        classifier=classifier
    )
    results = dataframe(results)
    export_df(
        results,
        config.RESULTS_CSV,
        get_output_dir(
            root,
            version=version,
            config_sha=config.normalized_script_hash(),
        )
    )


def _return_empty_set(subject: Subject, hunk: pygit2.DiffHunk) -> set[str]:
    return set()