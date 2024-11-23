#!/usr/bin/env python

from urllib import parse

from arrsync.common import JobType
from arrsync.utils import _assert_never


def initialize(job_type: JobType, url: str) -> str:
    if job_type is JobType.Sonarr:
        return parse.urljoin(url, "initialize.json")
    if job_type is JobType.Radarr:
        return parse.urljoin(url, "initialize.json")
    if job_type is JobType.Lidarr:
        return parse.urljoin(url, "initialize.json")
    else:
        _assert_never(job_type)


def status(job_type: JobType, url: str) -> str:
    if job_type is JobType.Sonarr:
        return parse.urljoin(url, "api/v3/system/status")
    if job_type is JobType.Radarr:
        return parse.urljoin(url, "api/v3/system/status")
    if job_type is JobType.Lidarr:
        return parse.urljoin(url, "api/v1/system/status")
    else:
        _assert_never(job_type)


def content(job_type: JobType, url: str) -> str:
    if job_type is JobType.Sonarr:
        return parse.urljoin(url, "api/v3/series")
    if job_type is JobType.Radarr:
        return parse.urljoin(url, "api/v3/movie")
    if job_type is JobType.Lidarr:
        return parse.urljoin(url, "api/v1/artist")
    else:
        _assert_never(job_type)


def profile(job_type: JobType, url: str) -> str:
    if job_type is JobType.Sonarr:
        return parse.urljoin(url, "api/v3/qualityprofile")
    if job_type is JobType.Radarr:
        return parse.urljoin(url, "api/v3/qualityprofile")
    if job_type is JobType.Lidarr:
        return parse.urljoin(url, "api/v1/qualityprofile")
    else:
        _assert_never(job_type)


def tag(job_type: JobType, url: str) -> str:
    if job_type is JobType.Sonarr:
        return parse.urljoin(url, "api/v3/tag")
    if job_type is JobType.Radarr:
        return parse.urljoin(url, "api/v3/tag")
    if job_type is JobType.Lidarr:
        return parse.urljoin(url, "api/v1/tag")
    else:
        _assert_never(job_type)


def language(job_type: JobType, url: str) -> str:
    if job_type is JobType.Sonarr:
        return parse.urljoin(url, "api/v3/languageprofile")
    if job_type is JobType.Radarr:
        return parse.urljoin(url, "api/v3/language")
    if job_type is JobType.Lidarr:
        raise Exception(f"{job_type} does not support language")
    else:
        _assert_never(job_type)


def metadata(job_type: JobType, url: str) -> str:
    if job_type is JobType.Lidarr:
        return parse.urljoin(url, "api/v1/metadataprofile")
    if job_type is JobType.Radarr:
        raise Exception(f"{job_type} does not support metadata")
    if job_type is JobType.Sonarr:
        raise Exception(f"{job_type} does not support metadata")
    else:
        _assert_never(job_type)
