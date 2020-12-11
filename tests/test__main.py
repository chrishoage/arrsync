import logging
from argparse import Namespace

from pytest_mock import MockerFixture

from arrsync.__main__ import main


def test__main(mocker: MockerFixture) -> None:
    mock_create_config_parser = mocker.patch("arrsync.__main__.create_config_parser")
    mock_parse_args = mocker.patch("arrsync.__main__.parse_args")
    mock_set_debug_level = mocker.patch("arrsync.__main__.set_debug_level")
    mock_cli_main = mocker.patch("arrsync.__main__.cli.main")

    spy = mocker.spy(mock_create_config_parser, "read_file")
    mock_create_config_parser.return_value = mock_create_config_parser
    mock_parse_args.return_value = Namespace(
        config="config.conf", debug=False, dry_run=False
    )

    main(["--config", "config.conf"])

    mock_create_config_parser.assert_called_once()
    spy.assert_called_once_with("config.conf")
    mock_cli_main.assert_called_once_with(mock_create_config_parser, False)

    mocker.resetall()

    mock_parse_args.return_value = Namespace(
        config="config.conf", debug=True, dry_run=False
    )

    main(["--config", "config.conf", "--debug"])

    mock_set_debug_level.assert_called_once_with(logging.DEBUG)

    mocker.resetall()

    mock_parse_args.return_value = Namespace(
        config="config.conf", debug=False, dry_run=True
    )

    main(["--config", "config.conf", "--dry-run"])

    mock_cli_main.assert_called_once_with(mock_create_config_parser, True)
