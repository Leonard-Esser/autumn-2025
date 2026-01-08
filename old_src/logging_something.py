import logging
from logging.handlers import TimedRotatingFileHandler

from pathlib import Path

def setup_logging(root: Path) -> None:
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logs_dir = root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    file_handler = TimedRotatingFileHandler(
        logs_dir / "autumn-2025.log",
        when="midnight",
        interval=1,
        backupCount=180,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)