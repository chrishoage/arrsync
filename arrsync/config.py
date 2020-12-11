#!/usr/bin/env python

import argparse
import configparser
import logging
import os
from typing import Any, Optional

logging.basicConfig(
    level=os.environ.get("SYNCARR_DEBUG_LEVEL", logging.INFO),
    datefmt="%Y-%m-%d %H:%M:%S",
    format="[%(asctime)s] %(levelname)-6s %(message)s",
)


logger = logging.getLogger()


def create_config_parser() -> configparser.ConfigParser:
    return configparser.ConfigParser(default_section="common", strict=True)


def parse_args(args: Optional[Any] = None) -> argparse.Namespace:

    arg_parser = argparse.ArgumentParser(
        prog="arrsync",
        description="Sync missing content between Sonarr, Radarr, and Lidarr instances",
    )

    arg_parser.add_argument(
        "-c",
        "--config",
        type=argparse.FileType("r"),
        required=True,
        help="Configuration file to use",
    )

    arg_parser.add_argument(
        "--debug", action="store_true", help="Print debug messages to stdout"
    )

    arg_parser.add_argument(
        "--dry-run", action="store_true", help="Do not sync anything"
    )

    return arg_parser.parse_args(args=args)


def set_debug_level(level: int) -> None:
    logger.setLevel(level)
