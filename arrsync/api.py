#!/usr/bin/env python

from __future__ import annotations

from typing import Any, Dict

from requests.models import Response
from requests.sessions import Session

from arrsync import routes
from arrsync.common import (
    ContentItem,
    ContentItems,
    JobType,
    Language,
    Languages,
    LidarrContent,
    Profile,
    Profiles,
    RadarrContent,
    SonarrContent,
    Status,
    Tag,
    Tags,
)
from arrsync.config import logger


class Api(object):
    session: Session
    job_type: JobType
    url: str

    def __init__(
        self, job_type: JobType, url: str, api_key: str, headers: Dict[str, str] = {}
    ):
        self.session = Session()
        self.job_type = job_type
        self.url = self._normalize_url(url)

        self.session.headers.update({"X-Api-Key": api_key, **headers})

    def __enter__(self) -> Api:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.session.close()

    def _normalize_url(self, url: str) -> str:
        return url if url.endswith("/") else f"{url}/"

    def _response_json(self, response: Response, url: str) -> Any:
        if not response.ok:
            raise Exception(
                f"failed to check status for {url} got {response.status_code}"
            )

        if not response.text:
            logger.error("%s response_text: %s", url, response.text)
            raise Exception(
                f"no response in status for {url}. Is the server set up correctly?"
            )

        return response.json()

    def get(self, url: str) -> Any:
        response = self.session.get(url=url)
        return self._response_json(response=response, url=url)

    def post(self, url: str, json: Dict[Any, Any]) -> Any:
        response = self.session.post(url=url, json=json)
        return self._response_json(response=response, url=url)

    def status(self) -> Status:
        full_url = routes.status(job_type=self.job_type, url=self.url)
        json = self.get(url=full_url)
        return Status.parse_obj(json)

    def profile(self) -> Profiles:
        full_url = routes.profile(job_type=self.job_type, url=self.url)
        json = self.get(url=full_url)
        return list(map(Profile.parse_obj, json))

    def tag(self) -> Tags:
        full_url = routes.tag(job_type=self.job_type, url=self.url)
        json = self.get(url=full_url)
        return list(map(Tag.parse_obj, json))

    def language(self) -> Languages:
        # Only Sonarr supports setting languageProfileId
        if self.job_type != JobType.Sonarr:
            return []

        full_url = routes.language(job_type=self.job_type, url=self.url)
        json = self.get(url=full_url)
        return list(map(Language.parse_obj, json))

    def metadata(self) -> Profiles:
        # Only Lidarr supports setting metadataProfileId
        if self.job_type != JobType.Lidarr:
            return []

        full_url = routes.metadata(job_type=self.job_type, url=self.url)
        json = self.get(url=full_url)
        return list(map(Profile.parse_obj, json))

    def content(self) -> ContentItems:
        full_url = routes.content(job_type=self.job_type, url=self.url)
        json = self.get(url=full_url)

        if self.job_type == JobType.Sonarr:
            return list(map(SonarrContent.parse_obj, json))
        if self.job_type == JobType.Radarr:
            return list(map(RadarrContent.parse_obj, json))
        if self.job_type == JobType.Lidarr:
            return list(map(LidarrContent.parse_obj, json))

        raise TypeError(f"{self.job_type} JobType is unhandled")

    def save(self, content_item: ContentItem) -> Any:
        full_url = routes.content(job_type=self.job_type, url=self.url)
        return self.post(url=full_url, json=content_item.dict(by_alias=True))
