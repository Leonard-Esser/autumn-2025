import argparse
import logging
import os
from collections.abc import Callable

import pygit2
from transformers.utils import logging as hf_logging

import config
from dead_channel_detector import dead_channel_detector
from detect_channels import detect_channels
from domain_model import Subject
from get_root import get_root
from get_version import get_version
from is_ccdc_event import is_ccdc_event
from main_pipeline import pipeline
from naysayer import naysayer
from play_sound import play_sound
from set_up_logging import set_up_logging
from testing import test_each_truth_file

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

# Silence HuggingFace logging
hf_logging.set_verbosity_error()

# Optional: silence Python logging from transformers/tokenizers
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("tokenizers").setLevel(logging.ERROR)

logger = logging.getLogger(__name__)

root = get_root()
program_version = get_version(root)

channel_detector: Callable[[Subject, pygit2.DiffHunk], set[str]] = detect_channels
if config.CANNOT_DETECT_ANYTHING:
    channel_detector = dead_channel_detector

def _is_ccdc_event(subject: Subject, hunk: pygit2.DiffHunk) -> bool:
    return is_ccdc_event(
        subject=subject,
        hunk=hunk,
        model_id=config.MODEL_ID,
        token_limit=config.TOKEN_LIMIT,
        task_mode=config.TASK_MODE,
        tries_to_classify_flattened_hunk=config.TRIES_TO_CLASSIFY_FLATTENED_HUNK,
        returns_asap=config.RETURNS_ASAP,
        logs_scores=config.LOGS_SCORES,
    )


classifier: Callable[[Subject, pygit2.DiffHunk], bool] = _is_ccdc_event
if config.IS_NAYSAYER:
    classifier = naysayer


def main():
    _prepare()
    
    args = build_parser().parse_args()
    if args.test:
        logger.info("Program is in test mode.")
        test_each_truth_file(
            root,
            channel_detector=channel_detector,
            classifier=classifier,
            logs_progress=config.LOGS_PROGRESS,
            deletes_git_dir_immediately=config.DELETES_GIT_DIR_IMMEDIATELY,
            program_version=program_version,
        )
    else:
        pipeline(
            root,
            channel_detector=channel_detector,
            classifier=classifier,
            logs_progress=config.LOGS_PROGRESS,
            deletes_git_dir_immediately=config.DELETES_GIT_DIR_IMMEDIATELY,
            program_version=program_version,
        )
    _finish()


def _prepare():
    set_up_logging(root)
    logger.info(f"Program version: {program_version}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--test",
        action="store_true",
        help="Run the program in test mode.",
    )
    return p


def _finish():
    play_sound()


if __name__ == "__main__":
    main()