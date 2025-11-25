import pygit2

from decorators import explain_why
import config


@explain_why
def get_diff(
    commit: pygit2.Commit,
    call_find_similar_right_away: bool = True
) -> pygit2.Diff:
    """Gets the diff that describes the changes introduced by a commit.

    Args:
        commit (pygit2.Commit): The commit.
        call_find_similar_right_away (bool, optional): Whether or not find_similar() is applied to the diff object right away. Defaults to True.

    Returns:
        pygit2.Diff: The diff "caused by the commit".
    """
    parent_tree = commit.parents[0].tree if commit.parent_ids else None
    
    swap = True
    # swap must be set to True.
    # Otherwise, the diff would describe what is necessary to undo the effects of the commit
    diff = commit.tree.diff_to_tree(
        parent_tree,
        flags=_get_flags_for_diff_options(),
        context_lines=config.CONTEXT_LINES,
        swap=swap
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
) -> str:
    changes = []
    for hunk in patch.hunks:
        for line in hunk.lines:
            changes.append(f"{line.origin} {line.content.rstrip()}")
    return changes


def flatten(
    changes: list[str]
) -> str:
    return "\n".join(changes)