#!/usr/bin/env python

from typing import List, TypeVar, Union

from arrsync.common import ContentItem, JobType, Language, LidarrContent, Profile, Tag

T = TypeVar("T", Tag, Profile, Language)


def find_in_list(input_list: List[T], query: str) -> Union[T, None]:
    return next(
        (
            item
            for item in input_list
            if str(item.id) == query or item.normalized_title() == query.lower()
        ),
        None,
    )


def find_ids_in_list(
    input_list: Union[List[Tag], List[Profile], List[Language]], opt_list: List[str]
) -> List[str]:
    normalized_list = list(map(lambda i: i.lower(), opt_list))
    return list(
        map(
            lambda i: str(i.id),
            [
                item
                for item in input_list
                if (
                    str(item.id) in normalized_list
                    or item.normalized_title() in normalized_list
                )
            ],
        )
    )


def get_debug_title(item: ContentItem) -> str:
    if isinstance(item, LidarrContent):
        return item.artist_name

    return item.title


def get_search_missing_attribute(job_type: JobType) -> str:
    if job_type == JobType.Sonarr:
        return "searchForMissingEpisodes"
    if job_type == JobType.Radarr:
        return "searchForMovie"
    if job_type == JobType.Lidarr:
        return "searchForMissingAlbums"

    raise TypeError(f"{job_type} JobType is unhandled")
