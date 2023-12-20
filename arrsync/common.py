#!/usr/bin/env python

import configparser
from abc import abstractmethod
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.networks import AnyHttpUrl
from typing_extensions import Annotated

Headers = Dict[str, str]
TagList = List[str]
ProfileList = List[str]


class JobType(Enum):
    Sonarr = "sonarr"
    Radarr = "radarr"
    Lidarr = "lidarr"


class BaseSyncJob(BaseModel):
    name: str
    type: JobType
    source_url: AnyHttpUrl
    source_key: str
    source_headers: Headers = {}
    source_tag_exclude: TagList = []
    source_tag_include: TagList = []
    source_profile_include: ProfileList = []
    source_profile_exclude: ProfileList = []
    dest_url: AnyHttpUrl
    dest_key: str
    dest_headers: Headers = {}
    dest_path: str
    dest_profile: str
    dest_search_missing: bool = False
    dest_monitor: bool = False

    @field_validator("type", mode="before")
    def type_from_option(cls, opt: str) -> JobType:  # noqa: N805
        return JobType(opt)

    @field_validator(
        "source_tag_include",
        "source_tag_exclude",
        "source_profile_include",
        "source_profile_exclude",
        mode="before",
    )
    def list_from_option(cls, opt: str) -> List[str]:  # noqa: N805
        return [] if not opt else [item.strip() for item in opt.split(",")]

    @field_validator("source_headers", "dest_headers", mode="before")
    def dict_from_option(cls, opt: str) -> Headers:  # noqa: N805
        headers: Dict[str, str] = {}

        config = OptDictConfigParser(strict=True)

        # Add a section so we can look up the header config options
        headers_string = f"[headers]\n{opt}"

        config.read_string(headers_string)
        headers_section = config["headers"]

        for option in headers_section:
            headers[option] = headers_section[option]

        return headers

    model_config = ConfigDict(extra="forbid")


class SonarrSyncJob(BaseSyncJob):
    type: Literal[JobType.Sonarr] = JobType.Sonarr
    dest_language_profile: Optional[str] = None


class RadarrSyncJob(BaseSyncJob):
    type: Literal[JobType.Radarr] = JobType.Radarr
    source_include_missing: Optional[bool] = None


class LidarrSyncJob(BaseSyncJob):
    type: Literal[JobType.Lidarr] = JobType.Lidarr
    dest_metadata_profile: Optional[str] = None


SyncJob = Union[SonarrSyncJob, RadarrSyncJob, LidarrSyncJob]


class ContentImage(BaseModel):
    cover_type: Annotated[str, Field(..., alias="coverType")]
    remote_url: Annotated[str, Field(..., alias="remoteUrl")]


class BaseContent(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    monitored: bool
    tags: List[int]
    quality_profile_id: Annotated[int, Field(..., alias="qualityProfileId")]
    root_folder_path: Optional[
        Annotated[str, Field(None, alias="rootFolderPath")]
    ] = None
    add_options: Optional[
        Annotated[
            Dict[str, Union[bool, str]],
            Field({}, alias="addOptions"),
        ]
    ] = {}

    @property
    @abstractmethod
    def _id_attr(self) -> Union[str, int]:
        pass

    def __hash__(self) -> int:
        return hash(self._id_attr)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, self.__class__):
            return self._id_attr == other._id_attr

        return NotImplemented


class SonarrContent(BaseContent):
    title: str
    title_slug: Annotated[str, Field(..., alias="titleSlug")]
    tvdb_id: Annotated[int, Field(..., alias="tvdbId")]
    tv_maze_id: Optional[Annotated[int, Field(None, alias="tvMazeId")]] = None
    tv_rage_id: Optional[Annotated[int, Field(None, alias="tvRageId")]] = None
    use_scene_numbering: Annotated[bool, Field(..., alias="useSceneNumbering")]
    season_folder: Annotated[bool, Field(..., alias="seasonFolder")]
    language_profile_id: Optional[
        Annotated[int, Field(None, alias="languageProfileId")]
    ] = None
    images: List[Optional[ContentImage]]
    seasons: Any

    @property
    def _id_attr(self) -> int:
        return self.tvdb_id


class RadarrContent(BaseContent):
    title: str
    title_slug: Annotated[str, Field(..., alias="titleSlug")]
    tmdb_id: Annotated[int, Field(..., alias="tmdbId")]
    imdb_id: Optional[Annotated[str, Field(None, alias="imdbId")]] = None
    year: int
    has_file: Annotated[bool, Field(..., alias="hasFile")]
    images: List[Optional[ContentImage]]

    @property
    def _id_attr(self) -> int:
        return self.tmdb_id


class LidarrContentImage(BaseModel):
    cover_type: str = Field(..., alias="coverType")
    url: str


class LidarrContent(BaseContent):
    artist_name: Annotated[str, Field(..., alias="artistName")]
    foreign_artist_id: Annotated[str, Field(..., alias="foreignArtistId")]
    metadata_profile_id: Optional[
        Annotated[int, Field(None, alias="metadataProfileId")]
    ] = None
    images: List[Optional[LidarrContentImage]]
    albums: Any = None

    @property
    def _id_attr(self) -> str:
        return self.foreign_artist_id


ContentItem = Union[SonarrContent, RadarrContent, LidarrContent]
ContentItems = List[ContentItem]


class Status(BaseModel):
    version: str


class Tag(BaseModel):
    label: str
    id: int

    def normalized_title(self) -> str:
        return self.label.lower()


Tags = List[Tag]


class Profile(BaseModel):
    name: str
    id: int

    def normalized_title(self) -> str:
        return self.name.lower()


Profiles = List[Profile]


class Language(BaseModel):
    name: str
    id: int

    def normalized_title(self) -> str:
        return self.name.lower()


Languages = List[Language]


class OptDictConfigParser(configparser.ConfigParser):
    def optionxform(self, optionstr: str) -> str:
        return optionstr
