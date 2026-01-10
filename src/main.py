import argparse
import logging
import os

import pygit2

import config
from detect_channels import detect_channels
from domain_model import Subject
from get_root import get_root
from get_version import get_version
from is_ccdc_event import is_ccdc_event
from main_pipeline import pipeline
from play_sound import play_sound
from set_up_logging import set_up_logging
from testing import test_each_truth_file

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

logger = logging.getLogger(__name__)

root = get_root()
program_version = get_version(root)


def main():
    _prepare()
    args = build_parser().parse_args()
    if args.test:
        logger.info("Program is in test mode.")
        test_each_truth_file(
            root,
            channel_detector=detect_channels,
            classifier=_is_ccdc_event,
            logs_progress=config.LOGS_PROGRESS,
            deletes_git_dir_immediately=config.DELETES_GIT_DIR_IMMEDIATELY,
            program_version=program_version,
        )
    else:
        pipeline()
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


def _is_ccdc_event(subject: Subject, hunk: pygit2.DiffHunk) -> bool:
    return is_ccdc_event(
        subject=subject,
        hunk=hunk,
        model_id=config.MODEL_ID,
        token_limit=config.TOKEN_LIMIT,
        tries_to_classify_flattened_hunk=config.TRIES_TO_CLASSIFY_FLATTENED_HUNK,
        logs_scores=config.LOGS_SCORES,
    )


def _finish():
    play_sound()


if __name__ == "__main__":
    main()