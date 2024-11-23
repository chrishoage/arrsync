#!/usr/bin/env python

from configparser import ConfigParser
from typing import List

from pydantic import ValidationError

from arrsync.common import JobType, LidarrSyncJob, RadarrSyncJob, SonarrSyncJob, SyncJob
from arrsync.config import logger
from arrsync.lib import start_sync_job


def get_sync_jobs(config: ConfigParser) -> List[SyncJob]:
    sync_jobs: List[SyncJob] = []

    for section_name in config.sections():
        section = config[section_name]

        job_opts = {"name": section_name}

        for option_name in section:
            job_opts[option_name] = section[option_name]

        try:
            job_type = JobType(job_opts["type"])

            if job_type == JobType.Sonarr:
                sync_jobs.append(SonarrSyncJob.model_validate(job_opts))
            elif job_type == JobType.Radarr:
                sync_jobs.append(RadarrSyncJob.model_validate(job_opts))
            elif job_type == JobType.Lidarr:
                sync_jobs.append(LidarrSyncJob.model_validate(job_opts))

        except ValidationError as e:
            logger.error("%s: config error", section_name)
            logger.error(e)
            raise

    return sync_jobs


def main(config: ConfigParser, dry_run: bool = False) -> None:
    sync_jobs = get_sync_jobs(config)
    logger.debug(sync_jobs)

    for job in sync_jobs:
        name = job.name
        try:
            logger.info("%s: starting", name)
            start_sync_job(job, dry_run)
            logger.info("%s: finished", name)
        except Exception as e:
            logger.error("%s: error", name)
            logger.error(e)
