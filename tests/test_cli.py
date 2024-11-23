#!/usr/bin/env python

import argparse
import configparser
import logging

import pytest
from pydantic import AnyHttpUrl, ValidationError
from pytest_mock import MockerFixture

from arrsync import cli
from arrsync.common import JobType, RadarrSyncJob
from arrsync.config import create_config_parser


def test_main(
    mocker: MockerFixture,
) -> None:
    mocked_start_sync_job = mocker.patch("arrsync.cli.start_sync_job")
    mocked_get_sync_jobs = mocker.patch("arrsync.cli.get_sync_jobs")

    job = RadarrSyncJob.model_validate(
        dict(
            name="sync",
            type=JobType.Radarr,
            source_url="http://host",
            source_key="aaa",
            dest_url="http://host2",
            dest_key="bbb",
            dest_path="/path",
            dest_profile="1",
        )
    )

    mocked_get_sync_jobs.return_value = [job]

    parser = argparse.ArgumentParser()

    parser.add_argument("--config")

    config = configparser.ConfigParser()

    cli.main(config)

    mocked_start_sync_job.assert_called_once_with(job, False)


def test_main_fail(
    mocker: MockerFixture,
    caplog: pytest.LogCaptureFixture,
) -> None:
    mocked_start_sync_job = mocker.patch("arrsync.cli.start_sync_job")
    mocked_get_sync_jobs = mocker.patch("arrsync.cli.get_sync_jobs")
    job = RadarrSyncJob.model_validate(
        dict(
            name="sync",
            type=JobType.Radarr,
            source_url="http://host",
            source_key="aaa",
            dest_url="http://host2",
            dest_key="bbb",
            dest_path="/path",
            dest_profile="1",
        )
    )

    mocked_get_sync_jobs.return_value = [job]

    mocked_start_sync_job.side_effect = Exception()

    parser = argparse.ArgumentParser()

    parser.add_argument("--config")

    config = configparser.ConfigParser()

    with caplog.at_level(logging.ERROR):
        cli.main(config)

    assert "sync: error" in caplog.text


def test_get_sync_jobs() -> None:
    test_config = """
[radarr-remote-to-local]
type=radarr
source_url = http://localhost:7878/
source_key = aaa
dest_url = http://localhost:7879/radarr
dest_key = bbb
dest_path = /movies
source_include_missing = 1

[sonarr-remote-to-local]
type=sonarr
source_url = http://localhost:8989
source_key = aaa
dest_url = http://localhost:8980/sonarr
dest_key = bbb
dest_path = /tv

[lidarr-remote-to-local]
type=lidarr
source_url = http://localhost:8686/
source_key = aaa
dest_url = http://localhost:8687/lidarr
dest_key = bbb
dest_path = /music


# Shared settings between all sync jobs
[common]
dest_search_missing = 0
dest_monitor = 1
source_headers =
  X-Test-Header-Id=aaa
  X-Test-Header-Secret=bbb
source_tag_exclude = no-sync
dest_profile = Any
  """

    config_parser = create_config_parser()

    config_parser.read_string(test_config)

    jobs = cli.get_sync_jobs(config_parser)

    assert jobs[0].model_dump() == {
        "name": "radarr-remote-to-local",
        "type": JobType.Radarr,
        "source_url": AnyHttpUrl("http://localhost:7878/"),
        "source_key": "aaa",
        "dest_url": AnyHttpUrl("http://localhost:7879/radarr"),
        "dest_key": "bbb",
        "dest_path": "/movies",
        "source_include_missing": True,
        "dest_search_missing": False,
        "dest_monitor": True,
        "source_headers": {
            "X-Test-Header-Id": "aaa",
            "X-Test-Header-Secret": "bbb",
        },
        "dest_headers": {},
        "source_tag_include": [],
        "source_tag_exclude": ["no-sync"],
        "source_profile_exclude": [],
        "source_profile_include": [],
        "dest_profile": "Any",
    }


def test_get_sync_jobs_fail_unknown_type() -> None:
    test_config = """
[radarr-remote-to-local]
type=unknown
"""

    config_parser = create_config_parser()

    config_parser.read_string(test_config)

    with pytest.raises(ValueError):
        cli.get_sync_jobs(config_parser)


def test_get_sync_jobs_fail_missing_values() -> None:
    test_config = """
[radarr-remote-to-local]
type=radarr
source_url=http://host/
dest_path=/path
"""

    config_parser = create_config_parser()

    config_parser.read_string(test_config)

    with pytest.raises(ValidationError):
        cli.get_sync_jobs(config_parser)


def test_get_sync_jobs_fail_invalid_values() -> None:
    test_config = """
[lidarr-remote-to-local]
type=lidarr
source_url = http://localhost:7878/
source_key = aaa
dest_url = http://localhost:7879/radarr
dest_key = bbb
dest_path = /music
source_include_missing = 1
"""

    config_parser = create_config_parser()

    config_parser.read_string(test_config)

    with pytest.raises(ValidationError):
        cli.get_sync_jobs(config_parser)


def test_get_sync_jobs_allow_missing_key() -> None:
    test_config = """
[radarr-remote-to-local]
type=radarr
source_url=http://host/
dest_url=http://host2/
dest_path=/path
dest_profile=1
source_include_missing = 0
"""

    config_parser = create_config_parser()

    config_parser.read_string(test_config)

    jobs = cli.get_sync_jobs(config_parser)

    assert jobs[0].model_dump() == {
        "name": "radarr-remote-to-local",
        "type": JobType.Radarr,
        "source_url": AnyHttpUrl("http://host/"),
        "source_key": "",
        "dest_url": AnyHttpUrl("http://host2/"),
        "dest_key": "",
        "dest_path": "/path",
        "source_include_missing": False,
        "dest_search_missing": False,
        "dest_monitor": False,
        "source_headers": {},
        "dest_headers": {},
        "source_tag_include": [],
        "source_tag_exclude": [],
        "source_profile_exclude": [],
        "source_profile_include": [],
        "dest_profile": "1",
    }
