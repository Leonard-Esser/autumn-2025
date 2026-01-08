from collections import defaultdict
from collections.abc import Iterable

import pygit2


def flatten_lines(
    lines: Iterable[pygit2.DiffLine],
    origin_included: bool = False
) -> str:
    changes = []
    for line in lines:
        prefix = f"{line.origin} " if origin_included else ""
        changes.append(f"{prefix}{line.content.rstrip()}")
    return "\n".join(changes)


def flatten_hunk(
    hunk: pygit2.DiffHunk,
    origin_included: bool = False
) -> str:
    return flatten_lines(hunk.lines, origin_included)


def group_lines_by_origin(
    hunk: pygit2.DiffHunk
) -> dict[str, list[pygit2.DiffLine]]:
    buckets = defaultdict(list)
    for line in hunk.lines:
        buckets[line.origin].append(line)
    return dict(buckets)