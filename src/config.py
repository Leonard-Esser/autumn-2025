import hashlib
from datetime import datetime
from io import StringIO
from pathlib import Path
from tokenize import generate_tokens


def normalized_script_hash(length: int = 7) -> str:
    source = Path(__file__).read_text(encoding="utf-8")
    tokens = generate_tokens(StringIO(source).readline)
    normalized = "".join(
        tok.string for tok in tokens if tok.type != 61  # COMMENT
    )
    return hashlib.sha256(normalized.encode()).hexdigest()[:length]


# section: local variables
_README = "README"
_CONTRIBUTING = "CONTRIBUTING"
# end of section

# section: RE the subject
RANDOM_STATE = 42
NUMBER_OF_REPOS_TO_INVESTIGATE: int | None = None
SINCE: datetime | None = datetime(2023, 1, 1, 0, 0, 0)
# The datetime value of UNTIL has to be before the time of cloning a repo
UNTIL: datetime | None = datetime(2025, 12, 31, 23, 59, 59)
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
ONLY_CLASSIFY_THIS_MANY_COMMITS_PER_REPO: int | None = 10
# end of section

# section: program behavior
RETURNS_CACHED_DATA_IF_ANY = True
UPDATES_CACHE = True
CANNOT_DETECT_ANYTHING = False
IS_NAYSAYER = False
DELETES_GIT_DIR_IMMEDIATELY = False
# end of section

# section: diffing options
ASSUMES_MAXIMUM_OF_ONE_DELTA_PER_FILE = True
CONTEXT_LINES = 0
FINDS_SIMILAR = False
# end of section

# section: RE the Zero-shot classifier via NLI
# The model id of a predefined tokenizer hosted inside a model repo on huggingface.co.
MODEL_ID = "facebook/bart-large-mnli"
# Maximum allowed number of tokens for a single (premise, hypothesis) pair.
TOKEN_LIMIT = 512
TRIES_TO_CLASSIFY_FLATTENED_HUNK = False
# end of section

# section: logging
LOGS_SCORES = False
LOGS_EACH_PARTIAL_RESULT_CREATED = False
# end of section

# section: output
PARTS_OF_BASE_OUTPUT_DIR = [
    "data",
    "output"
]
SUBJECTS_CSV = "subjects.csv"
REPOS_CSV = "repos.csv"
COMMITS_CSV = "commits.csv"
RESULTS_CSV = "results.csv"
# end of section