from enum import Enum

class CCDEvent(Enum):
    CREATE = 1
    DELETE = 2
    UPDATE = 3
    MOVE = 4