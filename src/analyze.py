from collections.abc import Callable, Iterable
from pathlib import Path

import pygit2

from aggregate import aggregate
from decorators import stop_the_clock
from delete_git_dir import delete_git_dir
from domain_model import PartialResult, Result, Subject
from get_logger import get_logger
from get_patch import get_patch
from get_repo import get_repo

logger = get_logger(__name__)


@stop_the_clock
def analyze(
    subjects: Iterable[Subject],
    *,
    channel_detector: Callable[[Subject, pygit2.DiffHunk], set[str]],
    classifier: Callable[[Subject, pygit2.DiffHunk], bool],
    logs_progress: bool,
    deletes_git_dir_immediately: bool,
) -> set[Result]:
    """
    Groups subjects by repository and analyzes each subject.
    """
    if logs_progress:
        sample_size = len(subjects)
        counter: int = 1
    results: set[Result] = set()
    for full_name_of_repo, group_of_subjects in _group_subjects_by_repo(subjects).items():
        repo: pygit2.Repository = get_repo(full_name_of_repo)
        for subject in group_of_subjects:
            patch = get_patch(subject, repo)
            if logs_progress:
                logger.info((
                    f"Analyzing subject {counter} of {sample_size} – "
                    f"changes to {subject.path} "
                    f"introduced by commit {subject.commit_sha} "
                    f"at repo {subject.full_name_of_repo}"
                ))
            result = analyze_subject(
                subject,
                patch=patch,
                channel_detector=channel_detector,
                classifier=classifier,
            )
            if logs_progress:
                counter += 1
            results.add(result)
        if deletes_git_dir_immediately:
            delete_git_dir(Path(repo.path))
    return results


def _group_subjects_by_repo(subjects: Iterable[Subject]) -> dict[str, list[Subject]]:
    """
    Returns a dict mapping `full_name_of_repo` (e.g. "billz/raspap-webgui")
    to a list of subjects belonging to that repo, preserving input order.
    """
    grouped: dict[str, list[Subject]] = {}
    for subject in subjects:
        grouped.setdefault(subject.full_name_of_repo, []).append(subject)
    return grouped


@stop_the_clock
def analyze_subject(
    subject: Subject,
    *,
    patch: pygit2.Patch,
    channel_detector: Callable[[Subject, pygit2.DiffHunk], set[str]],
    classifier: Callable[[Subject, pygit2.DiffHunk], bool]
) -> Result:
    partial_results = [
        PartialResult(
            subject=subject,
            hunk=hunk,
            detected_channels=channel_detector(subject, hunk),
            is_ccdc_event=classifier(subject, hunk)
        )
        for hunk in patch.hunks
    ]
    if not partial_results:
        return Result(
            subject=subject,
            detected_channels=frozenset(),
            is_ccdc_event=False
        )
    return aggregate(partial_results)