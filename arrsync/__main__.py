#!/usr/bin/env python

import logging
from typing import Any, Optional

from arrsync import cli
from arrsync.config import create_config_parser, parse_args, set_debug_level


def main(args: Optional[Any] = None) -> None:
    args = parse_args(args=args)

    debug = True if args.debug else False
    dry_run = True if args.dry_run else False

    if debug:
        set_debug_level(logging.DEBUG)

    config_parser = create_config_parser()

    config_parser.read_file(args.config)

    cli.main(config_parser, dry_run)


if __name__ == "__main__":  # pragma: no cover
    main()
