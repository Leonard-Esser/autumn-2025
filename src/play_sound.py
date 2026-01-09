import platform
import subprocess


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
    play_sound()