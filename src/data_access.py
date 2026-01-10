from pathlib import Path

PARTS_OF_BASE_OUTPUT_DIR: list[str] = [
    "data",
    "output",
]

PARTS_OF_CACHE_DIR: list[str] = [
    *PARTS_OF_BASE_OUTPUT_DIR,
    "cache",
]

PARTS_OF_RESULTS_DIR: list[str] = [
    *PARTS_OF_BASE_OUTPUT_DIR,
    "results",
]

PARTS_OF_TESTS_DIR: list[str] = [
    *PARTS_OF_BASE_OUTPUT_DIR,
    "tests",
]

PARTS_OF_TRUTH_DIR: list[str] = [
    "data",
    "truth",
]


def get_output_dir(
    root: Path,
    *,
    child: str | None = None,
) -> Path:
    path = Path(root)
    for part in PARTS_OF_BASE_OUTPUT_DIR:
        path /= part
    if child:
        path /= child
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_cache_dir(
    root: Path,
    *,
    sample: str | None = None,
) -> Path:
    path = Path(root)
    for part in PARTS_OF_CACHE_DIR:
        path /= part
    if sample:
        path /= "samples"
        path /= f"sample_{sample}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_results_dir(
    root: Path,
    *,
    program_version: str | None = None,
    sample: str | None = None,
) -> Path:
    path = Path(root)
    for part in PARTS_OF_RESULTS_DIR:
        path /= part
    if program_version:
        path /= f"program_version_{program_version}"
    if sample:
        path /= f"sample_{sample}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_test_dir(
    root: Path,
    *,
    test: str,
) -> Path:
    path = Path(root)
    for part in PARTS_OF_TESTS_DIR:
        path /= part
    path /= f"test_{test}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_test_results_dir(
    root: Path,
    *,
    test: str,
    program_version: str | None = None,
) -> Path:
    path = Path(root)
    for part in PARTS_OF_TESTS_DIR:
        path /= part
    path /= f"test_{test}"
    path /= "test_results"
    if program_version:
        path /= f"program_version_{program_version}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_truth_dir(
    root: Path,
) -> Path:
    path = Path(root)
    for part in PARTS_OF_TRUTH_DIR:
        path /= part
    path.mkdir(parents=True, exist_ok=True)
    return path