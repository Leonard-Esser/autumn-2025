import random

from model import Event, EventWhereCommunicationChannelDocumentationHasChanged, TypeOfChange


def classify(
    repo: str,
    commit: str,
    path: str,
    flattened_changes: str
):
    return_dummy = random.choice([True, False])
    
    if return_dummy:
        return create_dummy(Event(repo, commit, path))
    else:
        return Event(repo, commit, path)


def create_dummy(base: Event):
    return EventWhereCommunicationChannelDocumentationHasChanged(
        base.get_repo(),
        base.get_commit(),
        base.get_path(),
        {
            "My Favorite Communication Channel": [TypeOfChange.ADD],
            "Another Communication Channel": [TypeOfChange.UPDATE],
            "The Communication Channel We All Hate": [TypeOfChange.REMOVE],
            "GitHub Issues": [TypeOfChange.MENTION_BY_NAME],
        }
    )