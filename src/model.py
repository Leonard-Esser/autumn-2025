from enum import Enum


class Event:
    def __init__(self, repo, commit, path):
        self.__repo = repo
        self.__commit = commit
        self.__path = path
    
    def get_repo(self):
        return self.__repo
    
    def get_commit(self):
        return self.__commit
    
    def get_path(self):
        return self.__path


class EventWhereCommunicationChannelDocumentationHasChanged(Event):
    def __init__(self, repo, commit, path, changes_per_channel):
        super().__init__(repo, commit, path)
        self.__changes_per_channel = changes_per_channel
    
    def get_changes_per_channel(self):
        return self.__changes_per_channel
    
    @property
    def does_not_affect_any_specific_channel(self):
        return (
            not self.__changes_per_channel
            or all(
                not changes
                for changes in self.__changes_per_channel.values()
            )
        )


class TypeOfChange(Enum):
    ADD = 1
    UPDATE = 2
    REMOVE = 3
    MENTION_BY_NAME = 4