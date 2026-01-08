from collections.abc import Callable

import pygit2
from aggregate import aggregate
from domain_model import PartialResult, Result, Subject


def analyze(
    subject: Subject,
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