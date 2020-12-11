#!/usr/bin/env python

import pytest

from arrsync.common import BaseContent, LidarrContent, RadarrContent, SonarrContent


def test_base_item_equality() -> None:
    a = BaseContent(
        monitored=False,
        tags=[],
        quality_profile_id=0,
    )

    b = BaseContent(
        monitored=False,
        tags=[],
        quality_profile_id=0,
    )

    with pytest.raises(NotImplementedError):
        assert a == b


def test_sonarr_item_equality() -> None:
    a = (
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
    )

    b = (
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
    )

    assert a == b
    assert a != {}


def test_radarr_item_equality() -> None:
    a = RadarrContent(
        title="One",
        title_slug="one",
        tmdb_id=1,
        year=2000,
        has_file=True,
        images=[],
        monitored=True,
        quality_profile_id=1,
        root_folder_path="/path",
        tags=[],
    )

    b = RadarrContent(
        title="One",
        title_slug="one",
        tmdb_id=1,
        year=2000,
        has_file=True,
        images=[],
        monitored=True,
        quality_profile_id=1,
        root_folder_path="/path",
        tags=[],
    )

    assert a == b
    assert a != {}


def test_lidarr_item_equality() -> None:
    a = LidarrContent(
        artist_name="One",
        foreign_artist_id="1",
        images=[],
        monitored=False,
        albums=[{"title": "Season 1", "attr": 10}],
        quality_profile_id=10,
        root_folder_path="/path",
        tags=[],
    )

    b = LidarrContent(
        artist_name="One",
        foreign_artist_id="1",
        images=[],
        monitored=False,
        albums=[{"title": "Season 1", "attr": 10}],
        quality_profile_id=10,
        root_folder_path="/path",
        tags=[],
    )

    assert a == b
    assert a != {}
