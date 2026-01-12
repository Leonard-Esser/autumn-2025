import pygit2

from domain_model import Subject


def naysayer(subject: Subject, hunk: pygit2.DiffHunk) -> bool:
    return False