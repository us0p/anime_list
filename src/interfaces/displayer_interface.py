from abc import ABC, abstractmethod
from typing import Generic, TypeVar, TypedDict

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

T = TypeVar("T")

class IDisplayer(ABC, Generic[T]):
    anime_inf: T

    @abstractmethod
    def render_info(self):
        ...
