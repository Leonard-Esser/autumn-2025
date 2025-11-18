import pygit2

import config


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
        raise Exception("We assume that there can be a maximum of one pygit2.DiffDelta per file.")


def flatten(
    patch: pygit2.Patch
) -> str:
    changes = []
    for hunk in patch.hunks:
        for line in hunk.lines:
            changes.append(f"{line.origin} {line.content.rstrip()}")
    return "\n".join(changes)


def file_is_part_of_diff(
    diff: pygit2.Diff,
    path: str
) -> bool:
    for delta in diff.deltas:
        if delta.old_file.path == path or delta.new_file.path == path:
            return True
    return False


def get_single_delta(
    diff: pygit2.Diff,
    path: str
) -> pygit2.DiffDelta:
    deltas_per_file = []
    for delta in diff.deltas:
        if delta.old_file.path == path or delta.new_file.path == path:
            deltas_per_file.append(delta)
    if config.ASSUME_MAXIMUM_OF_ONE_DELTA_PER_FILE:
        raise_exception_if_too_many_deltas_per_file(deltas_per_file)
    return deltas_per_file[0]