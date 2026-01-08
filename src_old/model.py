from enum import Enum


class EventKey:
    def __init__(
        self,
        full_name_of_repo,
        commit_sha,
        path
    ):
        self.__full_name_of_repo = full_name_of_repo
        self.__commit_sha = commit_sha
        self.__path = path
    
    @property
    def get_full_name_of_repo(self):
        return self.__full_name_of_repo
    
    @property
    def get_commit_sha(self):
        return self.__commit_sha
    
    @property
    def get_path(self):
        return self.__path


class Event:
    def __init__(self, key):
        self.__key = key
    
    @property
    def get_key(self):
        return self.__key


class CCDCEvent(Event):
    def __init__(
        self,
        key,
        types_of_change = None,
        affected_channels = None
    ):
        super().__init__(key)
        self.__types_of_change = types_of_change
        self.__affected_channels = affected_channels
    
    @property
    def get_types_of_change(self):
        return self.__types_of_change
    
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