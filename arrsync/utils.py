#!/usr/bin/env python

from typing import List, NoReturn, Optional, TypeVar, Union

from arrsync.common import ContentItem, JobType, Language, LidarrContent, Profile, Tag
from arrsync.config import logger

T = TypeVar("T", Tag, Profile, Language)


def _assert_never(x: NoReturn) -> NoReturn:
    assert False, "Unhandled type: {}".format(type(x).__name__)


def first_in_list(input_list: List[T]) -> Union[T, None]:
    """return the first item in input_list"""

    return next(iter(input_list), None)


def find_in_list(input_list: List[T], query: str) -> Union[T, None]:
    """Find an item in the input_list using query returning None if nothing is found"""

    return next(
        (
            item
            for item in input_list
            if str(item.id) == query or item.normalized_title() == query.lower()
        ),
        None,
    )


def find_in_list_with_fallback(
    input_list: List[T], query: Optional[str], list_name: str = "list"
) -> Union[T, None]:
    """Find the item in the input list using query. If none is found fall back to the first item in the list"""

    item = find_in_list(input_list, query) if query else None

    if item:
        return item

    if not item and query:
        logger.warning("unable to find '%s' in %s", query, list_name)

    return first_in_list(input_list)


def find_ids_in_list(
    input_list: Union[List[Tag], List[Profile], List[Language]], opt_list: List[str]
) -> List[str]:
    """Return the ids from the input_list using the opt_list"""

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
    if job_type is JobType.Sonarr:
        return "searchForMissingEpisodes"
    if job_type is JobType.Radarr:
        return "searchForMovie"
    if job_type is JobType.Lidarr:
        return "searchForMissingAlbums"
    else:
        _assert_never(job_type)
