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


RANDOM_STATE = 42

NUMBER_OF_REPOS_TO_INVESTIGATE: int | None = 50

_README = "README"
_CONTRIBUTING = "CONTRIBUTING"
FILES_TO_INVESTIGATE = [
    _README + ".md",
    _README.lower() + ".md",
    _README + ".txt",
    _README.lower() + ".txt",
    _CONTRIBUTING + ".md",
    _CONTRIBUTING.lower() + ".md",
    _CONTRIBUTING + ".txt",
    _CONTRIBUTING.lower() + ".txt",
]

COMMITS_SINCE: datetime | None = datetime(2023, 1, 1)

# The time of cloning a repo should be after COMMITS_UNTIL
COMMITS_UNTIL: datetime | None = datetime(2025, 12, 31, 23, 59, 59)

ONLY_CLASSIFY_THIS_MANY_COMMITS_PER_REPO: int | None = 3