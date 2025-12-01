from datetime import datetime

__all__ = [
    "DELETE_GIT_DIR_IMMEDIATELY",
    "SAMPLE_SIZE",
    "SINCE",
    "UNTIL",
    "PATHS_TO_CONSIDER",
    "PARTS_OF_BASE_OUTPUT_DIR",
    "NAME_OF_SAMPLES_DIR",
    "NAME_OF_COMMITS_DIR",
    "NAME_OF_FRAMES_DIR",
    "NAME_OF_CHANGES_DIR",
    "NAME_OF_RESULTS_DIR",
    "ASSUME_MAXIMUM_OF_ONE_DELTA_PER_FILE",
    "CONTEXT_LINES",
]

DELETE_GIT_DIR_IMMEDIATELY = False
SAMPLE_SIZE = 100
SINCE = datetime(2010, 1, 1)
UNTIL = datetime(2025, 11, 30, 23, 59, 59)

_README = "README"
_CONTRIBUTING = "CONTRIBUTING"
PATHS_TO_CONSIDER = [
    _README + ".md",
    _README.lower() + ".md",
    _README + ".txt",
    _README.lower() + ".txt",
    _CONTRIBUTING + ".md",
    _CONTRIBUTING.lower() + ".md",
    _CONTRIBUTING + ".txt",
    _CONTRIBUTING.lower() + ".txt",
]

PARTS_OF_BASE_OUTPUT_DIR = [
    "data",
    "output"
]
NAME_OF_SAMPLES_DIR = "samples"
NAME_OF_COMMITS_DIR = "commits"
NAME_OF_FRAMES_DIR = "frames"
NAME_OF_CHANGES_DIR = "changes"
NAME_OF_RESULTS_DIR = "results"

# diffing options:
ASSUME_MAXIMUM_OF_ONE_DELTA_PER_FILE = True
CONTEXT_LINES = 5