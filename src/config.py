from datetime import datetime

__all__ = [
    "DELETE_GIT_DIR_IMMEDIATELY",
    "SAMPLE_SIZE",
    "SINCE",
    "UNTIL",
    "PATHS_TO_CONSIDER",
]

DELETE_GIT_DIR_IMMEDIATELY = False
SAMPLE_SIZE = 1
SINCE = datetime(2019, 1, 1)
UNTIL = datetime(2024, 12, 31, 23, 59, 59)

_README = "README"
PATHS_TO_CONSIDER = [
    _README + ".md",
    _README.lower() + ".md",
    _README + ".txt",
    _README.lower() + ".txt",
]