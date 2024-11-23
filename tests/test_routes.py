#!/usr/bin/env python

from contextlib import nullcontext as does_not_raise
from typing import Any, Union

import pytest

from arrsync import routes
from arrsync.common import JobType


@pytest.mark.parametrize(
    "job_type,url,expected,excpetion",
    [
        (JobType.Sonarr, "http://host/", "initialize.json", does_not_raise()),
        (JobType.Radarr, "http://host/", "initialize.json", does_not_raise()),
        (JobType.Lidarr, "http://host/", "initialize.json", does_not_raise()),
        (None, None, None, pytest.raises(Exception)),
    ],
)
def test_initialize(
    job_type: JobType, url: str, expected: Union[str, None], excpetion: Any
) -> None:
    with excpetion:
        assert routes.initialize(job_type, url) == f"{url}{expected}"


@pytest.mark.parametrize(
    "job_type,url,expected,excpetion",
    [
        (JobType.Sonarr, "http://host/", "api/v3/system/status", does_not_raise()),
        (JobType.Radarr, "http://host/", "api/v3/system/status", does_not_raise()),
        (JobType.Lidarr, "http://host/", "api/v1/system/status", does_not_raise()),
        (None, None, None, pytest.raises(Exception)),
    ],
)
def test_status(
    job_type: JobType, url: str, expected: Union[str, None], excpetion: Any
) -> None:
    with excpetion:
        assert routes.status(job_type, url) == f"{url}{expected}"


@pytest.mark.parametrize(
    "job_type,url,expected,excpetion",
    [
        (JobType.Sonarr, "http://host/", "api/v3/series", does_not_raise()),
        (JobType.Radarr, "http://host/", "api/v3/movie", does_not_raise()),
        (JobType.Lidarr, "http://host/", "api/v1/artist", does_not_raise()),
        (None, None, None, pytest.raises(Exception)),
    ],
)
def test_content(
    job_type: JobType, url: str, expected: Union[str, None], excpetion: Any
) -> None:
    with excpetion:
        assert routes.content(job_type, url) == f"{url}{expected}"


@pytest.mark.parametrize(
    "job_type,url,expected,excpetion",
    [
        (JobType.Sonarr, "http://host/", "api/v3/qualityprofile", does_not_raise()),
        (JobType.Radarr, "http://host/", "api/v3/qualityprofile", does_not_raise()),
        (JobType.Lidarr, "http://host/", "api/v1/qualityprofile", does_not_raise()),
        (None, None, None, pytest.raises(Exception)),
    ],
)
def test_profile(
    job_type: JobType, url: str, expected: Union[str, None], excpetion: Any
) -> None:
    with excpetion:
        assert routes.profile(job_type, url) == f"{url}{expected}"


@pytest.mark.parametrize(
    "job_type,url,expected,excpetion",
    [
        (JobType.Sonarr, "http://host/", "api/v3/tag", does_not_raise()),
        (JobType.Radarr, "http://host/", "api/v3/tag", does_not_raise()),
        (JobType.Lidarr, "http://host/", "api/v1/tag", does_not_raise()),
        (None, None, None, pytest.raises(Exception)),
    ],
)
def test_tag(
    job_type: JobType, url: str, expected: Union[str, None], excpetion: Any
) -> None:
    with excpetion:
        assert routes.tag(job_type, url) == f"{url}{expected}"


@pytest.mark.parametrize(
    "job_type,url,expected,excpetion",
    [
        (JobType.Sonarr, "http://host/", "api/v3/languageprofile", does_not_raise()),
        (JobType.Radarr, "http://host/", "api/v3/language", does_not_raise()),
        (JobType.Lidarr, None, None, pytest.raises(Exception)),
        (None, None, None, pytest.raises(Exception)),
    ],
)
def test_language(
    job_type: JobType, url: str, expected: Union[str, None], excpetion: Any
) -> None:
    with excpetion:
        assert routes.language(job_type, url) == f"{url}{expected}"


@pytest.mark.parametrize(
    "job_type,url,expected,excpetion",
    [
        (JobType.Sonarr, None, None, pytest.raises(Exception)),
        (JobType.Radarr, None, None, pytest.raises(Exception)),
        (JobType.Lidarr, "http://host/", "api/v1/metadataprofile", does_not_raise()),
        (None, None, None, pytest.raises(Exception)),
    ],
)
def test_metadata(
    job_type: JobType, url: str, expected: Union[str, None], excpetion: Any
) -> None:
    with excpetion:
        assert routes.metadata(job_type, url) == f"{url}{expected}"
