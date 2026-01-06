from __future__ import annotations
from collections.abc import Iterable

import pygit2
from pathlib import Path
from typing import Dict, List

import config
from analyze import analyze
from delete_git_dir import delete_git_dir
from domain_model import Result, Subject
from get_patch import get_patch
from get_repo import get_repo


def search_for_ccdc_events(
    subjects: Iterable[Subject],
    channel_detector: Callable[[Subject, pygit2.DiffHunk], set[str]],
    classifier: Callable[[Subject, pygit2.DiffHunk], bool]
) -> set[Result]:
    """
    Groups subjects by repository and analyzes each subject.
    """
    results: set[Result] = set()
    for full_name_of_repo, group_of_subjects in _group_subjects_by_repo(subjects).items():
        repo: pygit2.Repository = get_repo(full_name_of_repo)
        for subject in group_of_subjects:
            patch = get_patch(subject, repo)
            result = analyze(
                subject=subject,
                patch=patch,
                channel_detector=channel_detector,
                classifier=classifier,
            )
            results.add(result)
        if config.DELETES_GIT_DIR_IMMEDIATELY:
            delete_git_dir(Path(repo.path))
    return results


def _group_subjects_by_repo(subjects: Iterable[Subject]) -> Dict[str, List[Subject]]:
    """
    Returns a dict mapping `full_name_of_repo` (e.g. "billz/raspap-webgui")
    to a list of subjects belonging to that repo, preserving input order.
    """
    grouped: Dict[str, List[Subject]] = {}
    for subject in subjects:
        grouped.setdefault(subject.full_name_of_repo, []).append(subject)
    return grouped