from abc import ABC, abstractmethod
from typing import TypedDict

from aiohttp import ClientSession

from .displayer_interface import AnimeDetailedInfo, AnimeListItem

AnimeListReturn = TypedDict(
    "AnimeListReturn",
    {
        "anime_list": list[AnimeListItem],
        "page": int,
        "total_pages": int
    }
)

Genre = TypedDict(
    "Genre",
    {
        "id": int,
        "name": str
    }
)

class IService(ABC):
    @abstractmethod
    async def get_anime_list(
        self,
        session: ClientSession,
        page = 1
    ) -> AnimeListReturn:
        ...

    @abstractmethod
    async def get_anime_details(
        self,
        session: ClientSession, 
        api_id: int
    ) -> AnimeDetailedInfo:
        ...

    @abstractmethod
    async def get_anime_list_by_name(
        self,
        session: ClientSession,
        name: str
    ) -> AnimeListReturn:
        ...

    @abstractmethod
    async def get_genres_list(
        self,
        session: ClientSession
    ) -> list[Genre]:
        ...
