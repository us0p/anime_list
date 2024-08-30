from abc import ABC, abstractmethod
from typing import TypedDict

AnimeListItem = TypedDict("AnimeListItem", {
    "api_id": int,
    "title": str,
    "overview": str,
    "genres": list[str],
    "release_date": str,
    "cover_url": str,
})

Trailer = TypedDict("Trailer", {"name": str, "site": str, "link": str})

AnimeDetailedInfo = TypedDict("AnimeDetailedInfo", {
    "api_id": int,
    "title": str,
    "overview": str,
    "genres": list[str],
    "release_date": str,
    "cover_url": str,
    "episodes_count": int,
    "seasons_count": int,
    "status": str,
    "trailers": list[Trailer]
})

FormatedTitleMap = TypedDict("FormatedTitleMap", {
    "title": str,
    "original_title": str,
    "max_lines": int
})

class IAnimeInfoListItem(ABC):
    @property
    @abstractmethod
    def anime_inf(self) -> AnimeListItem:
        ...

class IAnimeDetailedInfo(ABC):
    @property
    @abstractmethod
    def anime_inf(self) ->AnimeDetailedInfo:
        ...

class IDisplayer(ABC):
    @abstractmethod
    def render_info(self):
        ...
