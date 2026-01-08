import pygit2

import config
from dataframe import commits_df, repos_df, results_df
from decorators import stop_the_clock
from detect_channels import detect_channels
from domain_model import Subject
from draw_subjects import draw_subjects
from export import export_df, get_output_dir
from get_root import get_root
from get_version import get_version
from is_ccdc_event import is_ccdc_event

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

    if config.CANNOT_DETECT_ANYTHING:
        channel_detector = _return_empty_set
    else:
        channel_detector = detect_channels
    
    if config.IS_NAYSAYER:
        classifier = _naysayer
    else:
        classifier = _is_ccdc_event
    
    results = results_df(
        subjects=subjects,
        channel_detector=channel_detector,
        classifier=classifier,
    )
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


def _naysayer(subject: Subject, hunk: pygit2.DiffHunk) -> bool:
    return False


def _is_ccdc_event(subject: Subject, hunk: pygit2.DiffHunk) -> bool:
    return is_ccdc_event(
        subject=subject,
        hunk=hunk,
        model_id=config.MODEL_ID,
        token_limit=config.TOKEN_LIMIT,
        tries_to_classify_flattened_hunk=config.TRIES_TO_CLASSIFY_FLATTENED_HUNK,
        logs_scores=config.LOGS_SCORES,
    )