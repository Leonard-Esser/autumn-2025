import platform
import subprocess
from get_root import get_root
from orchestration import pipeline
from setup_logging import setup_logging


def main():
    setup_logging(get_root())
    pipeline()


def play_sound() -> None:
    if platform.system() != "Darwin": # if not on macOS
        return

    try:
        subprocess.run(
            ["afplay", "/System/Library/Sounds/Glass.aiff"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass


if __name__ == "__main__":
    main()
    play_sound()