from get_root import get_root
from orchestration import pipeline
from setup_logging import setup_logging


def main():
    root = get_root()
    setup_logging(root)
    subjects = root / "data" / "subjects" / "subjects_since_2023_until_2025.csv"
    pipeline(subjects)


if __name__ == "__main__":
    main()