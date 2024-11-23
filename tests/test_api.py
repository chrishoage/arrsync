#!/usr/bin/env python

import json
from contextlib import nullcontext as does_not_raise
from typing import Any, Union, cast

import pytest
import responses
from pydantic import ValidationError
from pytest_mock.plugin import MockerFixture
from responses import RequestsMock

from arrsync import routes
from arrsync.api import Api
from arrsync.common import (
    ContentItem,
    JobType,
    LidarrContent,
    RadarrContent,
    SonarrContent,
)


@pytest.mark.parametrize(
    "url",
    [
        "http://host/",
        "http://host/",
        "http://host/",
        "http://host/route",
        "http://host/route",
        "http://host/route",
        "http://host/route/sub/",
        "http://host/route/sub/",
        "http://host/route/sub/",
    ],
)
def tets_api_normalize_url(url: str) -> None:
    with Api(job_type=JobType.Sonarr, url=url, api_key="aaa") as api:
        assert api.url.endswith("/")


def test_api_attaches_key() -> None:
    with Api(job_type=JobType.Sonarr, url="http://host", api_key="aaa") as api:
        assert api.session.headers.get("X-API-Key") == "aaa"


def test_api_attaches_headers() -> None:
    with Api(
        job_type=JobType.Sonarr,
        url="http://host",
        api_key="aaa",
        headers={"X-My-Header": "yes"},
    ) as api:
        assert api.session.headers.get("X-My-Other-Header") is None
        assert api.session.headers.get("X-My-Header") == "yes"


@pytest.mark.parametrize(
    "body",
    [
        ('{"key": "value"}'),
        ('{"key": 42}'),
        ('{"key": true}'),
        ('[{"one": 1}, {"one": true}]'),
        ("{}"),
        ("[]"),
    ],
)
def test_api_get_success(resp: RequestsMock, api: Api, body: str) -> None:
    url = f"{api.url}test"

    resp.add(
        responses.GET,
        url=url,
        body=body,
        content_type="application/json",
        status=200,
    )

    assert api.get(url) == json.loads(body)


@pytest.mark.parametrize(
    "body,status,expectation",
    [
        ("{}", 200, does_not_raise()),
        ("[]", 200, does_not_raise()),
        (ConnectionError(), 0, pytest.raises(ConnectionError)),
        ("", 400, pytest.raises(Exception)),
        (None, 200, pytest.raises(Exception)),
        ("", 200, pytest.raises(Exception)),
    ],
)
def test_api_get_fail(
    resp: RequestsMock, api: Api, body: Union[str, None], status: int, expectation: Any
) -> None:
    url = f"{api.url}test"

    resp.add(responses.GET, url=url, body=body, status=status)

    with expectation:
        api.get(url)


@pytest.mark.parametrize(
    "json_dict",
    [
        ({"key": "value"}),
        ({"key": 42}),
        ({"key": True}),
        ([{"one": 1}, {"one": True}]),
        ({}),
        ([]),
    ],
)
def test_api_post_success(resp: RequestsMock, api: Api, json_dict: Any) -> None:
    url = f"{api.url}test"

    resp.add(
        responses.POST,
        url=url,
        json=json_dict,
        match=[responses.matchers.json_params_matcher(json_dict)],
        status=200,
    )

    assert api.post(url, json_dict) == json_dict


@pytest.mark.parametrize(
    "body,status,expectation",
    [
        ("{}", 200, does_not_raise()),
        ("[]", 200, does_not_raise()),
        (ConnectionError(), 0, pytest.raises(ConnectionError)),
        ("", 400, pytest.raises(Exception)),
        (None, 200, pytest.raises(Exception)),
        ("", 200, pytest.raises(Exception)),
    ],
)
def test_api_post_fail(
    resp: RequestsMock, api: Api, body: Any, status: Any, expectation: Any
) -> None:
    resp.add(responses.POST, url=api.url, body=body, status=status)

    with expectation:
        api.post(api.url, {})


def test_api_initialize(resp: RequestsMock) -> None:
    full_url = routes.initialize(JobType.Sonarr, "http://host/")

    resp.add(
        responses.GET,
        url=full_url,
        json={"apiRoot": "/api/v3", "apiKey": "aaa", "urlBase": "/"},
    )

    with Api(
        job_type=JobType.Sonarr, url="http://host/", api_key="", headers={}
    ) as api:

        assert api.session.headers.get("X-Api-Key") == "aaa"

        resp.replace(responses.GET, url=full_url, json={})

        with pytest.raises(ValidationError):
            api.initialize()


def test_status(api: Api, resp: RequestsMock) -> None:
    full_url = routes.status(api.job_type, api.url)

    resp.add(responses.GET, url=full_url, json={"version": "3", "ignore": True})

    status = api.status()

    assert status.version == "3"
    assert not hasattr(status, "ignore")

    resp.replace(responses.GET, url=full_url, json={})

    with pytest.raises(ValidationError):
        api.status()


def test_tag(api: Api, resp: RequestsMock) -> None:
    full_url = routes.tag(api.job_type, api.url)

    resp.add(
        responses.GET,
        url=full_url,
        json=[{"label": "My Tag", "id": 0}, {"label": "Other Tag", "id": 42}],
    )

    tags = api.tag()

    assert len(tags) == 2
    assert tags[0].id == 0

    resp.replace(responses.GET, url=full_url, json=[])

    tags = api.tag()

    assert len(tags) == 0


def test_profile(api: Api, resp: RequestsMock) -> None:
    full_url = routes.profile(api.job_type, api.url)

    resp.add(
        responses.GET,
        url=full_url,
        json=[
            {"name": "HD-1080p", "id": 0, "cuttoff": 1},
            {"name": "4K", "id": 42},
        ],
    )

    profiles = api.profile()

    assert len(profiles) == 2
    assert profiles[0].id == 0

    resp.replace(responses.GET, url=full_url, json=[])

    profiles = api.profile()

    assert len(profiles) == 0


def test_metadata_profile(resp: RequestsMock) -> None:
    with Api(job_type=JobType.Sonarr, url="http://host/", api_key="aaa") as api:
        assert len(api.metadata()) == 0

    with Api(job_type=JobType.Radarr, url="http://host/", api_key="aaa") as api:
        assert len(api.metadata()) == 0

    with Api(job_type=JobType.Lidarr, url="http://host/", api_key="aaa") as api:
        full_url = routes.metadata(api.job_type, api.url)

        resp.add(
            responses.GET,
            url=full_url,
            json=[
                {
                    "name": "One",
                    "id": 0,
                    "releaseStatuses": [
                        {"allowed": True, "releaseStatus": {"id": 0, "name": "Unknown"}}
                    ],
                },
                {"name": "Two", "id": 42},
            ],
        )

        metadata = api.metadata()

        assert len(metadata) == 2
        assert metadata[1].id == 42
        assert not hasattr(metadata[0], "releaseStatuses")

        resp.replace(responses.GET, url=full_url, json=[])

        metadata = api.metadata()

        assert len(metadata) == 0


def test_language(resp: RequestsMock) -> None:
    with Api(job_type=JobType.Lidarr, url="http://host/", api_key="aaa") as api:
        assert len(api.language()) == 0

    with Api(job_type=JobType.Radarr, url="http://host/", api_key="aaa") as api:
        assert len(api.language()) == 0

    with Api(job_type=JobType.Sonarr, url="http://host/", api_key="aaa") as api:
        full_url = routes.language(api.job_type, api.url)

        resp.add(
            responses.GET,
            url=full_url,
            json=[
                {
                    "name": "English",
                    "id": 0,
                    "languages": [
                        {"allowed": True, "language": {"id": 0, "name": "Unknown"}}
                    ],
                },
                {"name": "Forign", "id": 42},
            ],
        )

        languages = api.language()

        assert len(languages) == 2
        assert languages[1].id == 42
        assert not hasattr(languages[0], "languages")

        resp.replace(responses.GET, url=full_url, json=[])

        languages = api.language()

        assert len(languages) == 0


@pytest.mark.parametrize(
    "file_body",
    ["tests/fixtures/sonarr_series.json"],
    indirect=True,
)
def test_sonarr_content(resp: RequestsMock, file_body: str) -> None:
    url = "http://host/route"
    job_type = JobType.Sonarr
    with Api(job_type=job_type, url=url, api_key="aaa") as api:
        full_url = routes.content(api.job_type, api.url)

        resp.add(
            responses.GET,
            url=full_url,
            body=file_body,
            content_type="application/json",
        )

        content_items = api.content()

        assert len(content_items) > 0

        item = content_items[0]

        assert isinstance(item, SonarrContent)

        assert isinstance(item.title, str)
        assert isinstance(item.tvdb_id, int)
        assert len(item.images) > 0
        assert hasattr(item.images[0], "remote_url")
        assert not hasattr(item.images[0], "url")
        assert hasattr(item, "seasons")


@pytest.mark.parametrize(
    "file_body",
    ["tests/fixtures/radarr_movie.json"],
    indirect=True,
)
def test_radarr_content(resp: RequestsMock, api: Api, file_body: str) -> None:
    url = "http://host/route"
    job_type = JobType.Radarr
    with Api(job_type=job_type, url=url, api_key="aaa") as api:
        full_url = routes.content(api.job_type, api.url)

        resp.add(
            responses.GET,
            url=full_url,
            body=file_body,
            content_type="application/json",
        )

        content_items = api.content()

        assert len(content_items) > 0

        item = content_items[0]

        assert isinstance(item, RadarrContent)

        assert isinstance(item.title, str)
        assert isinstance(item.tmdb_id, int)
        assert isinstance(item.year, int)
        assert len(item.images) > 0
        assert hasattr(item.images[0], "remote_url")
        assert not hasattr(item.images[0], "url")


@pytest.mark.parametrize(
    "file_body",
    ["tests/fixtures/lidarr_artist.json"],
    indirect=True,
)
def test_lidarr_content(resp: RequestsMock, file_body: str) -> None:
    url = "http://host/route"
    job_type = JobType.Lidarr
    with Api(job_type=job_type, url=url, api_key="aaa") as api:
        full_url = routes.content(api.job_type, api.url)

        resp.add(
            responses.GET,
            url=full_url,
            body=file_body,
            content_type="application/json",
        )

        content_items = api.content()

        assert len(content_items) > 0

        item = content_items[0]

        assert isinstance(item, LidarrContent)

        assert isinstance(item.artist_name, str)
        assert isinstance(item.foreign_artist_id, str)
        assert len(item.images) > 0
        assert hasattr(item.images[0], "url")


def test_unknown_content(mocker: MockerFixture, resp: RequestsMock) -> None:
    mock_route = mocker.patch("arrsync.api.routes")
    url = "http://host"
    route = "v3/new/path"
    mock_route.content.return_value = f"{url}/{route}"
    unknown_job_type = cast(JobType, "unknown")

    with Api(job_type=unknown_job_type, url=url, api_key="aaa") as api:
        resp.add(
            responses.GET,
            json={},
            url=f"{api.url}{route}",
        )
        with pytest.raises(Exception):
            api.content()


@pytest.mark.parametrize(
    "job_type,url,item",
    [
        (
            JobType.Sonarr,
            "http://host/",
            SonarrContent(
                title="One",
                title_slug="one",
                tvdb_id=1,
                images=[],
                monitored=False,
                use_scene_numbering=True,
                season_folder=True,
                seasons=[{"title": "Season 1", "attr": 10}],
                quality_profile_id=10,
                root_folder_path="/path",
                tags=[],
            ),
        ),
        (
            JobType.Radarr,
            "http://host/",
            RadarrContent(
                title="One",
                title_slug="one",
                tmdb_id=1,
                year=2000,
                has_file=True,
                images=[],
                monitored=False,
                quality_profile_id=10,
                root_folder_path="/path",
                tags=[],
            ),
        ),
        (
            JobType.Lidarr,
            "http://host/",
            LidarrContent(
                artist_name="One",
                foreign_artist_id="1",
                images=[],
                monitored=False,
                albums=[{"title": "Season 1", "attr": 10}],
                quality_profile_id=10,
                metadata_profile_id=1,
                root_folder_path="/path",
                tags=[],
            ),
        ),
    ],
)
def test_save_content(
    resp: RequestsMock, job_type: JobType, url: str, item: ContentItem
) -> None:
    with Api(job_type=job_type, url=url, api_key="aaa") as api:
        full_url = routes.content(job_type=job_type, url=api.url)
        resp.add(
            responses.POST,
            url=full_url,
            json=item.model_dump(),
            match=[
                responses.matchers.json_params_matcher(item.model_dump(by_alias=True))
            ],
            status=200,
        )
        api.save(item)
