#!/usr/bin/env python

import pytest
from mock import MagicMock
from pytest_mock import MockerFixture
from tests.conftest import CreateContentItem, CreateSyncJob

from arrsync.api import Api
from arrsync.common import (
    ContentItem,
    ContentItems,
    JobType,
    Language,
    Languages,
    LidarrContent,
    Profile,
    Profiles,
    SonarrContent,
    Status,
    Tag,
    Tags,
)
from arrsync.lib import (
    calculate_content_diff,
    get_content_payloads,
    start_sync_job,
    sync_content,
)
from arrsync.utils import _assert_never


def item_in_list(items: ContentItems, search_item: ContentItem) -> bool:
    return (
        next(
            (item for item in items if item._id_attr == search_item._id_attr),
            None,
        )
        is not None
    )


@pytest.mark.parametrize("job_type", [JobType.Sonarr, JobType.Radarr, JobType.Lidarr])
def test_calculate_content_diff(
    job_type: JobType,
    create_sync_job: CreateSyncJob,
    create_content_item: CreateContentItem,
) -> None:
    job = create_sync_job(job_type)

    item_one = create_content_item(job_type)
    item_two = create_content_item(job_type)

    source_content: ContentItems = [
        item_one,
        item_two,
    ]

    dest_content: ContentItems = [item_two]

    content_diff = calculate_content_diff(
        job=job,
        source_content=source_content,
        source_tags=[],
        source_profiles=[],
        dest_content=dest_content,
    )

    print(content_diff)

    assert len(content_diff) == 1
    assert item_in_list(content_diff, item_one)
    assert not item_in_list(content_diff, item_two)


@pytest.mark.parametrize("job_type", [JobType.Sonarr, JobType.Radarr, JobType.Lidarr])
def test_calculate_content_diff_tag_include(
    job_type: JobType,
    create_sync_job: CreateSyncJob,
    create_content_item: CreateContentItem,
) -> None:
    job = create_sync_job(job_type, source_tag_include="1, tag 4")

    source_tags: Tags = [
        Tag(label="Tag 1", id=1),
        Tag(label="Tag 2", id=2),
        Tag(label="Tag 3", id=3),
        Tag(label="Tag 4", id=4),
    ]

    item_one = create_content_item(
        job_type,
        tags=[1, 2],
    )
    item_two = create_content_item(
        job_type,
        tags=[3],
    )
    item_three = create_content_item(
        job_type,
        tags=[4],
    )
    item_four = create_content_item(job_type)

    source_content: ContentItems = [
        item_one,
        item_two,
        item_three,
        item_four,
    ]

    dest_content: ContentItems = []

    content_diff = calculate_content_diff(
        job=job,
        source_content=source_content,
        source_tags=source_tags,
        source_profiles=[],
        dest_content=dest_content,
    )

    assert len(content_diff) == 2
    assert item_in_list(content_diff, item_one)
    assert item_in_list(content_diff, item_three)
    assert not item_in_list(content_diff, item_two)
    assert not item_in_list(content_diff, item_four)


@pytest.mark.parametrize("job_type", [JobType.Sonarr, JobType.Radarr, JobType.Lidarr])
def test_calculate_content_diff_tag_exclude(
    job_type: JobType,
    create_sync_job: CreateSyncJob,
    create_content_item: CreateContentItem,
) -> None:
    job = create_sync_job(job_type, source_tag_exclude="1, tag 4")

    source_tags = [
        Tag(label="Tag 1", id=1),
        Tag(label="Tag 2", id=2),
        Tag(label="Tag 3", id=3),
        Tag(label="Tag 4", id=4),
    ]

    item_one = create_content_item(
        job_type,
        tags=[1, 2],
    )

    item_two = create_content_item(
        job_type,
        tags=[3],
    )

    item_three = create_content_item(
        job_type,
        tags=[4],
    )
    item_four = create_content_item(job_type)

    source_content: ContentItems = [
        item_one,
        item_two,
        item_three,
        item_four,
    ]

    dest_content: ContentItems = []

    content_diff = calculate_content_diff(
        job=job,
        source_content=source_content,
        source_tags=source_tags,
        source_profiles=[],
        dest_content=dest_content,
    )

    assert len(content_diff) == 2
    assert item_in_list(content_diff, item_two)
    assert item_in_list(content_diff, item_four)
    assert not item_in_list(content_diff, item_one)
    assert not item_in_list(content_diff, item_three)


def test_calculate_content_diff_radarr_skip_missing(
    create_sync_job: CreateSyncJob,
    create_content_item: CreateContentItem,
) -> None:
    job_type = JobType.Radarr
    job = create_sync_job(job_type)

    item_one = create_content_item(
        job_type,
        has_file=False,
    )

    item_two = create_content_item(
        job_type,
        has_file=True,
    )

    source_content: ContentItems = [
        item_one,
        item_two,
    ]

    dest_content: ContentItems = []

    content_diff = calculate_content_diff(
        job=job,
        source_content=source_content,
        source_tags=[],
        source_profiles=[],
        dest_content=dest_content,
    )

    assert len(content_diff) == 1
    assert not item_in_list(content_diff, item_one)
    assert item_in_list(content_diff, item_two)


def test_calculate_content_diff_radarr_include_missing(
    create_sync_job: CreateSyncJob,
    create_content_item: CreateContentItem,
) -> None:
    job_type = JobType.Radarr
    job = create_sync_job(job_type, source_include_missing=True)

    item_one = create_content_item(
        job_type,
        has_file=False,
    )

    item_two = create_content_item(
        job_type,
        has_file=True,
    )

    source_content: ContentItems = [
        item_one,
        item_two,
    ]

    dest_content: ContentItems = []

    content_diff = calculate_content_diff(
        job=job,
        source_content=source_content,
        source_tags=[],
        source_profiles=[],
        dest_content=dest_content,
    )

    assert len(content_diff) == 2
    assert item_in_list(content_diff, item_one)
    assert item_in_list(content_diff, item_two)


@pytest.mark.parametrize("job_type", [JobType.Sonarr, JobType.Radarr, JobType.Lidarr])
def test_calculate_content_quality_profile_include(
    job_type: JobType,
    create_sync_job: CreateSyncJob,
    create_content_item: CreateContentItem,
) -> None:
    job = create_sync_job(job_type, source_profile_include=" other one , 20")

    source_profiles: Profiles = [
        Profile(name="Any", id=1),
        Profile(name="Other One", id=10),
        Profile(name="Profile", id=20),
    ]

    item_one = create_content_item(job_type, quality_profile_id=1)
    item_two = create_content_item(job_type, quality_profile_id=10)
    item_three = create_content_item(job_type, quality_profile_id=20)

    source_content: ContentItems = [
        item_one,
        item_two,
        item_three,
    ]

    dest_content: ContentItems = []

    content_diff = calculate_content_diff(
        job=job,
        source_content=source_content,
        source_tags=[],
        source_profiles=source_profiles,
        dest_content=dest_content,
    )

    print(content_diff)

    assert len(content_diff) == 2
    assert item_in_list(content_diff, item_three)
    assert item_in_list(content_diff, item_two)
    assert not item_in_list(content_diff, item_one)


@pytest.mark.parametrize("job_type", [JobType.Sonarr, JobType.Radarr, JobType.Lidarr])
def test_calculate_content_quality_profile_exclude(
    job_type: JobType,
    create_sync_job: CreateSyncJob,
    create_content_item: CreateContentItem,
) -> None:
    job = create_sync_job(
        job_type,
        source_profile_exclude=" other one , 20",
    )

    source_profiles: Profiles = [
        Profile(name="Any", id=1),
        Profile(name="Other One", id=10),
        Profile(name="Profile", id=20),
    ]

    item_one = create_content_item(job_type, quality_profile_id=1)
    item_two = create_content_item(job_type, quality_profile_id=10)
    item_three = create_content_item(job_type, quality_profile_id=20)

    source_content: ContentItems = [
        item_one,
        item_two,
        item_three,
    ]

    content_diff = calculate_content_diff(
        job=job,
        source_content=source_content,
        source_tags=[],
        source_profiles=source_profiles,
        dest_content=[],
    )

    assert len(content_diff) == 1
    assert not item_in_list(content_diff, item_three)
    assert not item_in_list(content_diff, item_two)
    assert item_in_list(content_diff, item_one)


@pytest.mark.parametrize("job_type", [JobType.Sonarr, JobType.Radarr, JobType.Lidarr])
def test_get_content_payloads_no_dest_profile(
    job_type: JobType,
    create_sync_job: CreateSyncJob,
    create_content_item: CreateContentItem,
) -> None:
    job = create_sync_job(
        job_type,
        dest_profile="20",
    )

    profiles: Profiles = []

    item_one = create_content_item(job_type, quality_profile_id=1)

    content: ContentItems = [
        item_one,
    ]

    with pytest.raises(Exception):
        get_content_payloads(
            job=job,
            content=content,
            dest_profiles=profiles,
            dest_metadata_profiles=[],
            dest_languages=[],
        )


@pytest.mark.parametrize("job_type", [JobType.Sonarr, JobType.Radarr, JobType.Lidarr])
def test_get_content_payloads_dest_path(
    job_type: JobType,
    create_sync_job: CreateSyncJob,
    create_content_item: CreateContentItem,
) -> None:
    job = create_sync_job(
        job_type,
        dest_path="/data/path",
    )

    profiles: Profiles = [
        Profile(name="Any", id=1),
    ]

    item_one = create_content_item(job_type, root_folder_path="/old/path")

    content: ContentItems = [
        item_one,
    ]

    payloads = get_content_payloads(
        job=job,
        content=content,
        dest_profiles=profiles,
        dest_metadata_profiles=profiles,
        dest_languages=[],
    )

    payload = payloads[0]

    assert payload
    assert payload.root_folder_path == "/data/path"


@pytest.mark.parametrize("job_type", [JobType.Sonarr, JobType.Radarr, JobType.Lidarr])
def test_get_content_payloads_dest_profile(
    job_type: JobType,
    create_sync_job: CreateSyncJob,
    create_content_item: CreateContentItem,
) -> None:
    job = create_sync_job(
        job_type,
        dest_profile="20",
    )

    profiles: Profiles = [
        Profile(name="Any", id=1),
        Profile(name="Other One", id=10),
        Profile(name="Profile", id=20),
    ]

    item_one = create_content_item(job_type, quality_profile_id=1)

    content: ContentItems = [
        item_one,
    ]

    payloads = get_content_payloads(
        job=job,
        content=content,
        dest_profiles=profiles,
        dest_metadata_profiles=profiles,
        dest_languages=[],
    )

    payload = payloads[0]

    assert payload
    assert payload.quality_profile_id == 20


@pytest.mark.parametrize("job_type", [JobType.Sonarr, JobType.Radarr, JobType.Lidarr])
def test_get_content_payloads_monitored(
    job_type: JobType,
    create_sync_job: CreateSyncJob,
    create_content_item: CreateContentItem,
) -> None:
    job = create_sync_job(
        job_type,
        dest_monitor=True,
    )

    profiles: Profiles = [
        Profile(name="Any", id=1),
    ]

    item_one = create_content_item(job_type, monitored=False, quality_profile_id=10)

    content: ContentItems = [item_one]

    payloads = get_content_payloads(
        job=job,
        content=content,
        dest_profiles=profiles,
        dest_metadata_profiles=profiles,
        dest_languages=[],
    )

    payload = payloads[0]

    assert payload
    assert payload.monitored


@pytest.mark.parametrize("job_type", [JobType.Sonarr, JobType.Radarr, JobType.Lidarr])
def test_get_content_payloads_search_missing(
    job_type: JobType,
    create_sync_job: CreateSyncJob,
    create_content_item: CreateContentItem,
) -> None:
    job = create_sync_job(
        job_type,
        dest_search_missing=True,
    )

    profiles: Profiles = [
        Profile(name="Any", id=1),
    ]

    item_one = create_content_item(job_type)

    content: ContentItems = [item_one]

    payloads = get_content_payloads(
        job=job,
        content=content,
        dest_profiles=profiles,
        dest_metadata_profiles=profiles,
        dest_languages=[],
    )

    payload = payloads[0]

    assert payload
    assert payload.add_options

    if job_type is JobType.Sonarr:
        assert payload.add_options["searchForMissingEpisodes"]
    elif job_type is JobType.Radarr:
        assert payload.add_options["searchForMovie"]
    elif job_type is JobType.Lidarr:
        assert payload.add_options["searchForMissingAlbums"]
    else:
        _assert_never(job_type)


def test_get_content_payloads_sonarr_languages(
    create_sync_job: CreateSyncJob,
    create_content_item: CreateContentItem,
) -> None:
    job_type = JobType.Sonarr
    job = create_sync_job(job_type, dest_language_profile="2")

    profiles: Profiles = [
        Profile(name="Any", id=1),
    ]

    languages: Languages = [Language(name="English", id=1), Language(name="Test", id=2)]

    item_one = create_content_item(job_type, language_profile_id=1)

    content: ContentItems = [item_one]

    payloads = get_content_payloads(
        job=job,
        content=content,
        dest_profiles=profiles,
        dest_metadata_profiles=[],
        dest_languages=languages,
    )

    payload = payloads[0]

    assert isinstance(payload, SonarrContent)
    assert payload.language_profile_id == 2


def test_get_content_payloads_lidarr_metadata_profile(
    create_sync_job: CreateSyncJob,
    create_content_item: CreateContentItem,
) -> None:
    job_type = JobType.Lidarr
    job = create_sync_job(job_type, dest_metadata_profile="other")

    profiles: Profiles = [
        Profile(name="Any", id=1),
    ]

    metadata_profiles: Profiles = [
        Profile(name="Standard", id=1),
        Profile(name="Other", id=10),
    ]

    item_one = create_content_item(job_type, metadata_profile_id=1)

    content: ContentItems = [
        item_one,
    ]

    payloads = get_content_payloads(
        job=job,
        content=content,
        dest_profiles=profiles,
        dest_metadata_profiles=metadata_profiles,
        dest_languages=[],
    )

    payload = payloads[0]

    assert isinstance(payload, LidarrContent)
    assert payload.metadata_profile_id == 10


def test_get_content_payloads_lidarr_no_metdata_profile(
    create_sync_job: CreateSyncJob,
    create_content_item: CreateContentItem,
) -> None:
    job_type = JobType.Lidarr
    job = create_sync_job(job_type)

    profiles: Profiles = [
        Profile(name="Any", id=1),
    ]

    metadata_profiles: Profiles = []

    item_one = create_content_item(job_type, metadata_profile_id=1)

    content: ContentItems = [
        item_one,
    ]

    with pytest.raises(Exception):
        get_content_payloads(
            job=job,
            content=content,
            dest_profiles=profiles,
            dest_metadata_profiles=metadata_profiles,
            dest_languages=[],
        )


@pytest.mark.parametrize("job_type", [JobType.Sonarr, JobType.Radarr, JobType.Lidarr])
def test_sync_content(
    mocker: MockerFixture,
    job_type: JobType,
    create_content_item: CreateContentItem,
) -> None:
    item_one = create_content_item(job_type)

    content: ContentItems = [item_one]

    with Api(job_type=job_type, url="http://host", api_key="aaa") as api:
        dest_api = mocker.patch.object(target=api, attribute="save")
        dest_api.save.return_value = content[0].dict()

        sync_content(content=content, dest_api=dest_api)

        dest_api.save.assert_called_once_with(content_item=content[0])

        dest_api.save.return_value = None

        with pytest.raises(Exception):
            sync_content(content=content, dest_api=dest_api)


@pytest.mark.parametrize("job_type", [JobType.Sonarr, JobType.Radarr, JobType.Lidarr])
def test_sync_content_dry_run(
    mocker: MockerFixture,
    job_type: JobType,
    create_content_item: CreateContentItem,
) -> None:
    item_one = create_content_item(job_type)

    content: ContentItems = [item_one]

    with Api(job_type=job_type, url="http://host", api_key="aaa") as api:
        dest_api = mocker.patch.object(target=api, attribute="save")
        dest_api.save.return_value = content[0].dict()

        sync_content(content=content, dest_api=dest_api, dry_run=True)

        dest_api.save.assert_not_called()


@pytest.mark.parametrize("job_type", [JobType.Sonarr, JobType.Radarr, JobType.Lidarr])
def test_start_sync_job(
    mocker: MockerFixture,
    job_type: JobType,
    create_sync_job: CreateSyncJob,
) -> None:
    mock_sync_content = mocker.patch("arrsync.lib.sync_content")
    mock_get_content_payloads = mocker.patch("arrsync.lib.get_content_payloads")
    mock_calculate_content_diff = mocker.patch("arrsync.lib.calculate_content_diff")

    job = create_sync_job(job_type)

    source_api = MagicMock(spec=Api)
    source_api.__enter__.return_value = source_api
    source_api.status.return_value = Status.parse_obj({"version": "3"})

    dest_api = MagicMock(spec=Api)
    dest_api.__enter__.return_value = dest_api
    dest_api.status.return_value = Status.parse_obj({"version": "3"})

    mock_api = mocker.patch(
        "arrsync.lib.Api", autospec=True, side_effect=[source_api, dest_api]
    )

    start_sync_job(job)

    assert mock_api.call_count == 2
    source_api.status.assert_called_once_with()
    dest_api.status.assert_called_once_with()
    source_api.tag.assert_called_once_with()
    source_api.profile.assert_called_once_with()
    dest_api.profile.assert_called_once_with()
    dest_api.metadata.assert_called_once_with()
    dest_api.language.assert_called_once_with()
    source_api.content.assert_called_once_with()
    dest_api.content.assert_called_once_with()
    mock_calculate_content_diff.assert_called()
    mock_get_content_payloads.assert_called()
    mock_sync_content.assert_called()

    mock_api.reset_mock()
    source_api.reset_mock()
    dest_api.reset_mock()

    source_api = source_api
    source_api.__enter__.return_value = source_api
    source_api.status.return_value = None

    dest_api = dest_api
    dest_api.__enter__.return_value = dest_api
    dest_api.status.return_value = None

    mock_api.side_effect = [source_api, dest_api]

    with pytest.raises(Exception):
        start_sync_job(job)
