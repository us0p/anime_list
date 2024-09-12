from abc import ABC, abstractmethod
from typing import Optional
from datetime import date

from ..dtos.dto_tag import DTOTag
from ..dtos.dto_anime import DTOAnime

class MetaDB(type, ABC):
    instances_ = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls.instances_:
            cls.instances_[cls] = super().__call__(*args, **kwargs)
        return cls.instances_[cls]

class IDatabase(metaclass=MetaDB):
    @abstractmethod
    def select_all_tags(self) -> list[DTOTag]:
        ...

    @abstractmethod
    def update_anime(
        self,
        anime_id: int,
        last_season: Optional[int],
        last_episode: Optional[int],
        new_tag: Optional[int]
    ) -> Optional[DTOAnime]:
        ...

    @abstractmethod
    def delete_anime(self, anime_id: int) -> Optional[DTOAnime]:
        ...

    @abstractmethod
    def get_animes(self) -> list[DTOAnime]:
        ...

    @abstractmethod
    def get_anime_by_id(self, anime_id: int) -> Optional[DTOAnime]:
        ...

    @abstractmethod
    def select_animes_by_title(self, title: str) -> list[DTOAnime]:
        ...

    @abstractmethod
    def get_anime_by_tmdb_id(self, tmdb_id: int) -> Optional[DTOAnime]:
        ...

    @abstractmethod
    def insert_anime(
        self,
        anime_tmdb_id: int,
        seasons: int,
        watching_season: Optional[int],
        last_watched_episode: Optional[int],
        last_watched_at: Optional[date],
        title: str,
        tag_id: int
    ) -> Optional[int]:
        ...
