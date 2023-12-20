#!/usr/bin/env python

import logging

import pytest
from pytest_mock import MockFixture

from arrsync.config import parse_args, set_debug_level


def test_set_debug_level(mocker: MockFixture) -> None:
    mock_logger = mocker.patch("arrsync.config.logger")
    set_debug_level(logging.CRITICAL)
    mock_logger.setLevel.assert_called_with(logging.CRITICAL)


def test_parse_args_fails(mocker: MockFixture) -> None:
    with pytest.raises(SystemExit):
        parse_args()


def test_parse_args_config(mocker: MockFixture) -> None:
    mock_open = mocker.patch("builtins.open")

    parse_args(["--config", "config.conf"])
    args, kwargs = mock_open.call_args
    assert args[0] == "config.conf"

    mock_open.reset_mock()

    parse_args(["-c", "config.conf"])
    args, kwargs = mock_open.call_args
    assert args[0] == "config.conf"


def test_parse_args_debug(mocker: MockFixture) -> None:
    mocker.patch("builtins.open")

    args = parse_args(["--config", "tests/fixtures/config.conf", "--debug"])
    assert isinstance(args.debug, bool)
    assert args.debug is True


def test_parse_args_dry_run(mocker: MockFixture) -> None:
    mocker.patch("builtins.open")

    args = parse_args(["--config", "tests/fixtures/config.conf", "--dry-run"])
    assert isinstance(args.dry_run, bool)
    assert args.dry_run is True
