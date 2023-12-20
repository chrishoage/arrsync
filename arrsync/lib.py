#!/usr/bin/env python

import pprint

from arrsync.api import Api
from arrsync.common import (
    ContentItems,
    JobType,
    Languages,
    LidarrContent,
    Profiles,
    RadarrContent,
    RadarrSyncJob,
    SonarrContent,
    SyncJob,
    Tags,
)
from arrsync.config import logger
from arrsync.utils import (
    find_ids_in_list,
    find_in_list_with_fallback,
    get_debug_title,
    get_search_missing_attribute,
)

pp = pprint.PrettyPrinter()


def get_content_payloads(
    job: SyncJob,
    content: ContentItems,
    dest_profiles: Profiles,
    dest_metadata_profiles: Profiles,
    dest_languages: Languages,
) -> ContentItems:
    payload_items: ContentItems = []

    dest_profile = find_in_list_with_fallback(
        dest_profiles, job.dest_profile, "profiles"
    )

    if not dest_profile:
        raise Exception("A profile is required to be set an no profiles are available")

    for item in content:
        payload = item.model_copy(
            deep=True,
            update={
                "quality_profile_id": dest_profile.id,
                "root_folder_path": job.dest_path,
                "monitored": job.dest_monitor,
            },
        )

        if job.dest_search_missing:
            search_missing_attribute = get_search_missing_attribute(job.type)

            payload.add_options.update(
                {search_missing_attribute: job.dest_search_missing}
            )

        if isinstance(payload, SonarrContent) and job.type == JobType.Sonarr:
            dest_language = find_in_list_with_fallback(
                dest_languages, job.dest_language_profile, "languages"
            )

            if dest_language:
                payload.language_profile_id = dest_language.id

        if isinstance(payload, LidarrContent) and job.type == JobType.Lidarr:
            dest_metadata_profile = find_in_list_with_fallback(
                dest_metadata_profiles, job.dest_metadata_profile, "metadata profiles"
            )

            if dest_metadata_profile:
                payload.metadata_profile_id = dest_metadata_profile.id
            else:
                raise Exception(
                    "Lidarr requires a metadata profile to be set and no metadata profiles are available"
                )

        payload_items.append(payload)

    return payload_items


def sync_content(content: ContentItems, dest_api: Api, dry_run: bool = False) -> None:
    for item in content:
        post_json = None
        if not dry_run:
            post_json = dest_api.save(content_item=item)

        if not post_json and not dry_run:
            logger.error("failed to sync %s", get_debug_title(item))
            raise Exception(f"Failed to create {get_debug_title(item)}")
        else:
            logger.info(
                "synced %s%s", get_debug_title(item), " (dry-run)" if dry_run else ""
            )


def calculate_content_diff(
    job: SyncJob,
    source_content: ContentItems,
    source_tags: Tags,
    source_profiles: Profiles,
    dest_content: ContentItems,
) -> ContentItems:
    diff_content = list(set(source_content) - set(dest_content))
    filtered_content: ContentItems = []

    tag_include_ids = find_ids_in_list(source_tags, job.source_tag_include)
    tag_exclude_ids = find_ids_in_list(source_tags, job.source_tag_exclude)

    quality_profile_include_ids = find_ids_in_list(
        source_profiles, job.source_profile_include
    )
    quality_profile_exclude_ids = find_ids_in_list(
        source_profiles, job.source_profile_exclude
    )

    for item in diff_content:
        if tag_exclude_ids and (
            set(map(lambda t: str(t), item.tags)) & set(tag_exclude_ids)
        ):
            logger.debug(
                "skipping %s: source_tag_exclude source (%s) config (%s)",
                get_debug_title(item),
                item.tags,
                tag_exclude_ids,
            )
            continue

        if tag_include_ids and not (
            set(map(lambda t: str(t), item.tags)) & set(tag_include_ids)
        ):
            logger.debug(
                "skipping %s: source_tag_include source (%s) config (%s)",
                get_debug_title(item),
                item.tags,
                tag_include_ids,
            )
            continue

        if (
            quality_profile_exclude_ids
            and str(item.quality_profile_id) in quality_profile_exclude_ids
        ):
            logger.debug(
                "skipping %s: source_profile_exclude source (%s) config (%s)",
                get_debug_title(item),
                item.quality_profile_id,
                quality_profile_exclude_ids,
            )
            continue

        if (
            quality_profile_include_ids
            and str(item.quality_profile_id) not in quality_profile_include_ids
        ):
            logger.debug(
                "skipping %s: source_profile_include source (%s) config (%s)",
                get_debug_title(item),
                item.quality_profile_id,
                quality_profile_include_ids,
            )
            continue

        if isinstance(job, RadarrSyncJob) and isinstance(item, RadarrContent):
            if not job.source_include_missing and not item.has_file:
                logger.debug(
                    "skipping %s: source_include_missing is False",
                    get_debug_title(item),
                )
                continue

        logger.debug("including %s", get_debug_title(item))
        filtered_content.append(item)

    return filtered_content


def start_sync_job(job: SyncJob, dry_run: bool = False) -> None:
    logger.debug("starting %s job", job.name)

    with Api(
        job_type=job.type,
        url=str(job.source_url),
        api_key=job.source_key,
        headers=job.source_headers,
    ) as source_api, Api(
        job_type=job.type,
        url=str(job.dest_url),
        api_key=job.dest_key,
        headers=job.dest_headers,
    ) as dest_api:
        source_status = source_api.status()
        dest_status = dest_api.status()

        if not source_status or not dest_status:
            logger.error("failed %s job", job.name)
            raise Exception("failed to check stauts")

        source_tags = source_api.tag()

        source_profiles = source_api.profile()

        dest_profiles = dest_api.profile()

        dest_metadata_profiles = dest_api.metadata()

        dest_languages = dest_api.language()

        source_content = source_api.content()

        dest_content = dest_api.content()

        content_diff = calculate_content_diff(
            job=job,
            source_content=source_content,
            source_tags=source_tags,
            source_profiles=source_profiles,
            dest_content=dest_content,
        )

        content_payloads = get_content_payloads(
            job=job,
            content=content_diff,
            dest_profiles=dest_profiles,
            dest_metadata_profiles=dest_metadata_profiles,
            dest_languages=dest_languages,
        )

        sync_content(content=content_payloads, dest_api=dest_api, dry_run=dry_run)
