from typing import Any, Iterator, Protocol

import pytest
import responses
from _pytest.fixtures import FixtureRequest, SubRequest

from arrsync.api import Api
from arrsync.common import (
    ContentItem,
    JobType,
    LidarrContent,
    LidarrSyncJob,
    RadarrContent,
    RadarrSyncJob,
    SonarrContent,
    SonarrSyncJob,
    SyncJob,
)
from arrsync.utils import _assert_never


class CreateSyncJob(Protocol):
    def __call__(self, job_type: JobType, **extra_attrs: Any) -> SyncJob:
        ...


@pytest.fixture(scope="function")
def create_sync_job(
    request: FixtureRequest,
) -> CreateSyncJob:
    def _create_sync_job(
        job_type: JobType,
        **extra_attrs: Any,
    ) -> SyncJob:
        base_attrs = {
            "name": "sync",
            "type": job_type,
            "source_url": "http://host",
            "source_key": "aaa",
            "dest_url": "http://host2",
            "dest_key": "bbb",
            "dest_path": "/path",
            "dest_profile": "1",
        }

        if job_type is JobType.Sonarr:
            return SonarrSyncJob.model_validate({**base_attrs, **extra_attrs})

        elif job_type is JobType.Radarr:
            return RadarrSyncJob.model_validate({**base_attrs, **extra_attrs})

        elif job_type is JobType.Lidarr:
            return LidarrSyncJob.model_validate({**base_attrs, **extra_attrs})

        else:
            _assert_never(job_type)

    return _create_sync_job


class CreateContentItem(Protocol):
    def __call__(self, job_type: JobType, **extra_attrs: Any) -> ContentItem:
        ...


@pytest.fixture(scope="function")
def create_content_item(
    request: FixtureRequest,
) -> CreateContentItem:
    count = 0

    def _create_content_item(job_type: JobType, **extra_attrs: Any) -> ContentItem:
        nonlocal count

        count += 1

        base_attrs = {
            "title": f"Item {count}",
            "title_slug": f"item-{count}",
            "images": [],
            "monitored": True,
            "quality_profile_id": 1,
            "root_folder_path": "/path",
            "tags": [],
        }

        if job_type is JobType.Radarr:
            return RadarrContent.model_validate(
                {
                    "tmdb_id": count,
                    "year": 2016,
                    "has_file": True,
                    **base_attrs,
                    **extra_attrs,
                }
            )

        elif job_type is JobType.Sonarr:
            return SonarrContent.model_validate(
                {
                    "tvdb_id": count,
                    "use_scene_numbering": True,
                    "season_folder": True,
                    "seasons": [{"title": "Season 1", "attr": 10}],
                    **base_attrs,
                    **extra_attrs,
                }
            )

        elif job_type is JobType.Lidarr:
            return LidarrContent.model_validate(
                {
                    "artist_name": f"Item {count}",
                    "foreign_artist_id": f"{count}",
                    "images": [],
                    "monitored": False,
                    "albums": [{"title": "Season 1", "attr": 10}],
                    "quality_profile_id": 1,
                    "root_folder_path": "/path",
                    "tags": [],
                    **extra_attrs,
                }
            )

        else:
            _assert_never(job_type)

    return _create_content_item


# responses does not currently offer types so we intentionally bail out of
# disallow-untyped-decorators here
@responses.activate
@pytest.fixture(scope="function")
def resp(request: FixtureRequest) -> Iterator[responses.RequestsMock]:
    with responses.RequestsMock() as resp:
        yield resp


@pytest.fixture(
    params=[
        ("http://host", JobType.Sonarr),
        ("http://host", JobType.Radarr),
        ("http://host", JobType.Lidarr),
    ]
)
def api(request: SubRequest) -> Iterator[Api]:
    url, job_type = request.param
    with Api(job_type=job_type, url=url, api_key="aaa") as api:
        yield api


@pytest.fixture(scope="function")
def file_body(request: SubRequest) -> Iterator[str]:
    with open(request.param) as file:
        yield file.read()
