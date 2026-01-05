import pygit2

from domain_model import Subject


def detect_channels(subject: Subject, hunk: pygit2.DiffHunk) -> set[str]:
    # TODO implement
    return set()