#!/usr/bin/env python

from contextlib import nullcontext as does_not_raise
from typing import Any, Dict, Union

import pytest
from tests.conftest import CreateContentItem

from arrsync.common import JobType, Profile, Tag
from arrsync.utils import (
    find_ids_in_list,
    find_in_list,
    get_debug_title,
    get_search_missing_attribute,
)


def test_find_job_tags() -> None:
    tags = [
        Tag(label="Tag 1", id=1),
        Tag(label="Tag 2", id=2),
        Tag(label="Tag 3", id=3),
        Tag(label="Tag 4", id=4),
    ]

    tag_list = ["1", "tag 4"]

    found_tag_ids = find_ids_in_list(tags, tag_list)

    assert "1" in found_tag_ids
    assert "4" in found_tag_ids


def test_find_job_profiles() -> None:
    profiles = [
        Profile(name="Profile 1", id=1),
        Profile(name="Profile 2", id=2),
        Profile(name="Profile 3", id=3),
        Profile(name="Profile 4", id=4),
    ]

    profile_list = ["1", "profile 4"]

    found_profile_ids = find_ids_in_list(profiles, profile_list)

    assert "1" in found_profile_ids
    assert "4" in found_profile_ids


@pytest.mark.parametrize(
    "query,result",
    [
        ("1", {"name": "Profile 1", "id": 1}),
        ("profile 4", {"name": "Profile 4", "id": 4}),
        ("PROFILE 3", {"name": "Profile 3", "id": 3}),
        ("Profile 2", {"name": "Profile 2", "id": 2}),
        ("nope", None),
    ],
)
def test_find_job_profile(query: str, result: Dict[str, Any]) -> None:
    profiles = [
        Profile(name="Profile 1", id=1),
        Profile(name="Profile 2", id=2),
        Profile(name="Profile 3", id=3),
        Profile(name="Profile 4", id=4),
    ]

    found_profile = find_in_list(profiles, query)

    assert result == found_profile


@pytest.mark.parametrize(
    "query,result",
    [
        ("1", {"label": "Tag 1", "id": 1}),
        ("tag 4", {"label": "Tag 4", "id": 4}),
        ("TAG 3", {"label": "Tag 3", "id": 3}),
        ("Tag 2", {"label": "Tag 2", "id": 2}),
        ("nope", None),
    ],
)
def test_find_job_tag(query: str, result: Dict[str, Any]) -> None:
    profiles = [
        Tag(label="Tag 1", id=1),
        Tag(label="Tag 2", id=2),
        Tag(label="Tag 3", id=3),
        Tag(label="Tag 4", id=4),
    ]

    found_profile = find_in_list(profiles, query)

    assert result == found_profile


@pytest.mark.parametrize(
    "job_type,expected,excpetion",
    [
        (JobType.Sonarr, "searchForMissingEpisodes", does_not_raise()),
        (JobType.Radarr, "searchForMovie", does_not_raise()),
        (JobType.Lidarr, "searchForMissingAlbums", does_not_raise()),
        (None, None, pytest.raises(Exception)),
    ],
)
def test_get_search_missing_attribute(
    job_type: JobType, expected: Union[str, None], excpetion: Any
) -> None:
    with excpetion:
        assert get_search_missing_attribute(job_type) == expected


@pytest.mark.parametrize("job_type", [JobType.Sonarr, JobType.Radarr, JobType.Lidarr])
def test_get_debug_title(
    job_type: JobType,
    create_content_item: CreateContentItem,
) -> None:
    assert get_debug_title(create_content_item(job_type)) == "Item 1"
