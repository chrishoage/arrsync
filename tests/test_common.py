#!/usr/bin/env python


from arrsync.common import LidarrContent, RadarrContent, SonarrContent


def test_sonarr_item_equality() -> None:
    a = SonarrContent(
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
    )

    b = SonarrContent(
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
