from get_root import get_root
from orchestration import pipeline
from setup_logging import setup_logging


def main():
    setup_logging(get_root())
    pipeline()


if __name__ == "__main__":
    main()