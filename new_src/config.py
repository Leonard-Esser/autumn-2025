from datetime import datetime
from typing import Optional


# section: local variables
_README = "README"
_CONTRIBUTING = "CONTRIBUTING"
# end of section

# section: RE the subject
RANDOM_STATE = 42
NUMBER_OF_REPOS_TO_INVESTIGATE: Optional[int] = 10
SINCE = datetime(2023, 1, 1)
UNTIL = datetime(2025, 12, 31, 23, 59, 59)
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
# end of section

# section: program behavior
IS_NAYSAYER = True
DELETES_GIT_DIR_IMMEDIATELY = False
# end of section

# section: diffing options
ASSUMES_MAXIMUM_OF_ONE_DELTA_PER_FILE = True
CONTEXT_LINES = 0
FINDS_SIMILAR = True
# end of section

# section: RE the Zero-shot classifier via NLI
# The model id of a predefined tokenizer hosted inside a model repo on huggingface.co.
MODEL_ID = "facebook/bart-large-mnli"
# Maximum allowed number of tokens for a single (premise, hypothesis) pair.
MAX_NUMBER_OF_TOKENS = 512
TRIES_TO_CLASSIFY_HUNK_WITH_ONLY_ONE_CALL = False
# end of section

# section: logging
LOGS_EACH_PARTIAL_RESULT_CREATED = False
# end of section

# section: output
PARTS_OF_BASE_OUTPUT_DIR = [
    "data",
    "output"
]
EXPORTS_SUBJECTS = True
SUBJECTS_DIR = "subjects"
# end of section