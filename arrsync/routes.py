#!/usr/bin/env python

from urllib import parse

from arrsync.common import JobType


def status(job_type: JobType, url: str) -> str:
    if job_type == JobType.Sonarr:
        return parse.urljoin(url, "api/v3/system/status")
    if job_type == JobType.Radarr:
        return parse.urljoin(url, "api/v3/system/status")
    if job_type == JobType.Lidarr:
        return parse.urljoin(url, "api/v1/system/status")

    raise TypeError(f"{job_type} JobType is unhandled")


def content(job_type: JobType, url: str) -> str:
    if job_type == JobType.Sonarr:
        return parse.urljoin(url, "api/v3/series")
    if job_type == JobType.Radarr:
        return parse.urljoin(url, "api/v3/movie")
    if job_type == JobType.Lidarr:
        return parse.urljoin(url, "api/v1/artist")

    raise TypeError(f"{job_type} JobType is unhandled")


def profile(job_type: JobType, url: str) -> str:
    if job_type == JobType.Sonarr:
        return parse.urljoin(url, "api/v3/qualityprofile")
    if job_type == JobType.Radarr:
        return parse.urljoin(url, "api/v3/qualityprofile")
    if job_type == JobType.Lidarr:
        return parse.urljoin(url, "api/v1/qualityprofile")

    raise TypeError(f"{job_type} JobType is unhandled")


def tag(job_type: JobType, url: str) -> str:
    if job_type == JobType.Sonarr:
        return parse.urljoin(url, "api/v3/tag")
    if job_type == JobType.Radarr:
        return parse.urljoin(url, "api/v3/tag")
    if job_type == JobType.Lidarr:
        return parse.urljoin(url, "api/v1/tag")

    raise TypeError(f"{job_type} JobType is unhandled")


def language(job_type: JobType, url: str) -> str:
    if job_type == JobType.Sonarr:
        return parse.urljoin(url, "api/v3/languageprofile")
    if job_type == JobType.Radarr:
        return parse.urljoin(url, "api/v3/language")
    if job_type == JobType.Lidarr:
        raise Exception(f"{job_type} does not support language")

    raise TypeError(f"{job_type} JobType is unhandled")


def metadata(job_type: JobType, url: str) -> str:
    if job_type == JobType.Lidarr:
        return parse.urljoin(url, "api/v1/metadataprofile")
    if job_type == JobType.Radarr:
        raise Exception(f"{job_type} does not support metadata")
    if job_type == JobType.Sonarr:
        raise Exception(f"{job_type} does not support metadata")

    raise TypeError(f"{job_type} JobType is unhandled")
