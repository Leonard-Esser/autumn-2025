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


class CCDCEvent(Event):
    def __init__(
        self,
        repo,
        commit,
        path,
        types_of_changes = None,
        affected_channels = None
    ):
        super().__init__(repo, commit, path)
        self.__types_of_changes = types_of_changes
        self.__affected_channels = affected_channels
    
    @property
    def get_types_of_changes(self):
        return self.__types_of_changes
    
    @property
    def get_affected_channels(self):
        return self.__affected_channels


class TypeOfChange(Enum):
    ADD = 1
    UPDATE = 2
    REMOVE = 3


def convert_to_type_of_change(value) -> TypeOfChange:
    if isinstance(value, TypeOfChange):
        return value

    if isinstance(value, str):
        v = value.strip()

        if v.isdigit():
            return TypeOfChange(int(v))

        if v.startswith("TypeOfChange."):
            v = v.split(".", 1)[1]

        return TypeOfChange[v]

    if isinstance(value, (int, float)):
        return TypeOfChange(int(value))

    raise ValueError(f"Cannot convert {value!r} to TypeOfChange")