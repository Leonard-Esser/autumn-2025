import pygit2

from decorators import explain_why
import config


def get_diff(
    commit: pygit2.Commit,
    context_lines: int,
    call_find_similar_right_away: bool = True
) -> pygit2.Diff:
    """Gets the diff describing the changes introduced by a commit."""

    flags = _get_flags_for_diff_options()
    swap = True
    parent_exists = bool(commit.parent_ids)

    if parent_exists:
        parent_tree = commit.parents[0].tree
        diff = commit.tree.diff_to_tree(
            parent_tree,
            flags=flags,
            context_lines=context_lines,
            swap=swap,
        )
    else:
        diff = commit.tree.diff_to_tree(
            flags=flags,
            context_lines=context_lines,
            swap=swap,
        )

    if call_find_similar_right_away:
        diff.find_similar()

    return diff


def _get_flags_for_diff_options(just_use_normal_flag: bool = False) -> int:
    if just_use_normal_flag:
        return pygit2.enums.DiffOption.NORMAL
    
    return (
        pygit2.enums.DiffOption.INCLUDE_TYPECHANGE |
        pygit2.enums.DiffOption.IGNORE_FILEMODE |
        pygit2.enums.DiffOption.IGNORE_BLANK_LINES |
        pygit2.enums.DiffOption.FORCE_TEXT |
        pygit2.enums.DiffOption.IGNORE_WHITESPACE
    )


def get_patch(
    diff: pygit2.Diff,
    path: str
):
    patches_relating_to_file = []
    for patch in diff:
        if patch_relates_to_file(patch, path):
            patches_relating_to_file.append(patch)
    if config.ASSUME_MAXIMUM_OF_ONE_DELTA_PER_FILE:
        raise_exception_if_too_many_deltas_per_file(patches_relating_to_file)
    return patches_relating_to_file[0]


def patch_relates_to_file(
    patch: pygit2.Patch,
    path: str
):
    return patch.delta.old_file.path == path or patch.delta.new_file.path == path


def raise_exception_if_too_many_deltas_per_file(
    deltas: list[pygit2.DiffDelta] | list[pygit2.Patch]
):
    if len(deltas) > 1:
        raise Exception("We assume that there can be a maximum of one pygit2.DiffDelta per file")


def get_changes(
    patch: pygit2.Patch
) -> list[str]:
    changes = []
    for hunk in patch.hunks:
        changes.extend(
            get_changes_of_hunk(hunk)
        )
    return changes


def get_changes_of_hunk(
    hunk: pygit2.DiffHunk
) -> list[str]:
    changes = []
    for line in hunk.lines:
        changes.append(f"{line.origin} {line.content.rstrip()}")
    return changes


def flatten(
    changes: list[str]
) -> str:
    return "\n".join(changes)


def get_flattened_changes_grouped_by_line_origin(
    hunk: pygit2.DiffHunk
) -> dict[str, str]:
    return _flatten_grouped_lines(
        _group_lines_by_origin(hunk),
        flatten
    )


from collections.abc import Callable

from typing import Any

def _flatten_grouped_lines(
    grouped_lines: dict[Any, list[str]],
    flatten: Callable[[list[str]], str],
) -> dict[Any, str]:
    return {
        key: flatten(lines)
        for key, lines in grouped_lines.items()
    }


def _group_lines_by_origin(
    hunk: pygit2.DiffHunk
) -> dict[str, list[str]]:
    from collections import defaultdict

    buckets = defaultdict(list)
    for line in hunk.lines:
        buckets[line.origin].append(line.content.rstrip())
    return dict(buckets)