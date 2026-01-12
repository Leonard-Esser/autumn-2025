import pygit2

from domain_model import Subject


def dead_channel_detector(subject: Subject, hunk: pygit2.DiffHunk) -> set[str]:
    return set()