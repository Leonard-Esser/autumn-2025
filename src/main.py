import os

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

from get_root import get_root
from orchestration import pipeline
from play_sound import play_sound
from setup_logging import setup_logging


def main():
    setup_logging(get_root())
    pipeline()


if __name__ == "__main__":
    main()
    play_sound()