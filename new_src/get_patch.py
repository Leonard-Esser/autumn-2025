import pygit2
from domain_model import Subject

import config


def get_patch(subject: Subject, repo: pygit2.Repository) -> pygit2.Patch:
    _assert_subject_matches_repo(subject, repo)
    diff = _get_diff(
        _get_commit(repo, subject.commit_sha),
        config.CONTEXT_LINES,
        config.FINDS_SIMILAR
    )
    patches_relating_to_file: list[pygit2.Patch] = []
    for patch in diff:
        if _patch_relates_to_file(patch, subject.path):
            patches_relating_to_file.append(patch)
    if config.ASSUMES_MAXIMUM_OF_ONE_DELTA_PER_FILE:
        _raise_exception_if_too_many_deltas_per_file(patches_relating_to_file)
    if not patches_relating_to_file:
        raise FileNotFoundError(
            f"No patch/delta found for path '{subject.path}' in commit {subject.commit_sha} "
            f"({subject.full_name_of_repo})."
        )
    return patches_relating_to_file[0]


def _assert_subject_matches_repo(subject: Subject, repo: pygit2.Repository) -> None:
    """
    Best-effort validation that the repo likely corresponds to subject.full_name_of_repo.
    If a remote named 'origin' exists, we check whether the full_name appears in its URL.
    If not, we do not hard-fail (to support local/bare repos without remotes).
    """
    try:
        origin = repo.remotes.get("origin")  # pygit2.Remote | None
    except Exception:
        origin = None
    if origin is None or not getattr(origin, "url", None):
        return
    remote_url = origin.url
    expected = subject.full_name_of_repo.strip()
    # Example remote_url: https://github.com/OWNER/REPO.git or git@github.com:OWNER/REPO.git
    # We just do a simple containment check to avoid over-parsing edge cases.
    if expected and expected not in remote_url:
        raise ValueError(
            (
                "Subject/repo mismatch: subject.full_name_of_repo does not appear "
                "in repo's origin URL. "
                f"subject.full_name_of_repo='{subject.full_name_of_repo}', "
                f"origin.url='{remote_url}'."
            )
        )


def _get_commit(repo: pygit2.Repository, commit_sha: str) -> pygit2.Commit:
    """
    Returns a pygit2.Commit from a SHA (or any rev-spec that revparse_single accepts).
    Raises a clear error if it can't be resolved to a Commit.
    """
    try:
        obj = repo.revparse_single(commit_sha)
    except KeyError as e:
        raise KeyError(f"Commit '{commit_sha}' not found in repository.") from e
    if not isinstance(obj, pygit2.Commit):
        raise TypeError(
            (
                f"revparse_single('{commit_sha}') returned {type(obj).__name__}, "
                "expected pygit2.Commit."
            )
        )
    return obj


def _get_diff(
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


def _patch_relates_to_file(
    patch: pygit2.Patch,
    path: str
):
    return patch.delta.old_file.path == path or patch.delta.new_file.path == path


def _raise_exception_if_too_many_deltas_per_file(
    deltas: list[pygit2.DiffDelta] | list[pygit2.Patch]
):
    if len(deltas) > 1:
        raise Exception("We assume that there can be a maximum of one pygit2.DiffDelta per file")