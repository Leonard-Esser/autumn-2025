from datetime import datetime
from typing import Optional


RANDOM_STATE = 42

SAMPLE_SIZE = 3

SINCE = datetime(2023, 1, 1)
UNTIL = datetime(2025, 12, 31, 23, 59, 59)

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

ONLY_CLASSIFY_THIS_MANY_COMMITS_PER_REPO: Optional[int] = 10

# diffing options
ASSUMES_MAXIMUM_OF_ONE_DELTA_PER_FILE = True
CONTEXT_LINES = 0
FINDS_SIMILAR = True

# The model id of a predefined tokenizer hosted inside a model repo on huggingface.co.
MODEL_ID = "facebook/bart-large-mnli"

# Maximum allowed number of tokens for a single (premise, hypothesis) pair.
MAX_NUMBER_OF_TOKENS = 512

LOGS_EACH_PARTIAL_RESULT_CREATED = True