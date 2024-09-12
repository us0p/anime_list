from datetime import date
from typing import Optional
from sqlalchemy import Engine, create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from ..interfaces.database_interface import IDatabase

from ..dtos.dto_anime import DTOAnime
from ..dtos.dto_tag import DTOTag

from ..models.anime import Anime
from ..models.base import Base
from ..models.tag import Tag
        
class Database(IDatabase):
    engine: Engine
    def __init__(self):
        self.engine = create_engine(
            "sqlite+pysqlite:///anime_list.db",
            echo=False
        )
        Base.metadata.create_all(self.engine)

    def select_all_tags(self) -> list[DTOTag]:
        with Session(self.engine) as session:
            tags = session.execute(select(Tag)).scalars().fetchall()
            return [self._crerate_dto_tag(tag) for tag in tags]

    def update_anime(
        self,
        anime_id: int,
        last_season: Optional[int],
        last_episode: Optional[int],
        new_tag: Optional[int]
    ) -> Optional[DTOAnime]:
        with Session(self.engine) as session:
            anime = session.get(Anime, anime_id)

            if not anime:
                return None

            if last_season:
                anime.watching_season = last_season
            if last_episode:
                anime.last_watched_episode = last_episode
            if new_tag:
                anime.tag_id = new_tag

            session.commit()
            return self._create_dto_anime(anime)

    def delete_anime(self, anime_id: int) -> Optional[DTOAnime]:
        with Session(self.engine) as session:
            anime = session.get(Anime, anime_id)
            if anime:
                session.delete(anime)
                session.commit()
                return self._create_dto_anime(anime)
            return None

    def get_animes(self) -> list[DTOAnime]:
        with Session(self.engine) as session:
            animes = session.execute(
                select(Anime)
                .options(joinedload(Anime.tag))
                .order_by(Anime.title)
            ).scalars().fetchall()

            return [self._create_dto_anime(a) for a in animes]

    def get_anime_by_id(self, anime_id: int) -> Optional[DTOAnime]:
        with Session(self.engine) as session:
            anime = session.execute(
                select(Anime)
                .where(Anime.id == anime_id)
                .options(joinedload(Anime.tag))
            ).scalar()
            if anime:
                return self._create_dto_anime(anime)
            return None

    def select_animes_by_title(self, title: str) -> list[DTOAnime]:
        with Session(self.engine) as session:
            animes = session.execute(
                select(Anime)
                .options(joinedload(Anime.tag))
                .where(Anime.title.ilike(f'%{title}%'))
            ).scalars().fetchall()

            return [self._create_dto_anime(anime) for anime in animes]

    def get_anime_by_tmdb_id(self, tmdb_id: int) -> Optional[DTOAnime]:
        with Session(self.engine) as session:
            anime = session.execute(
                select(Anime)
                .where(Anime.anime_tmdb_id == tmdb_id)
                .options(joinedload(Anime.tag))
            ).scalar()
            if anime:
                return self._create_dto_anime(anime)
            return None

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
        with Session(self.engine) as session:
            try:
                anime = Anime(
                    anime_tmdb_id=anime_tmdb_id,
                    seasons=seasons,
                    watching_season=watching_season,
                    last_watched_episode=last_watched_episode,
                    last_watched_at=last_watched_at,
                    title=title,
                    tag_id=tag_id
                )
                session.add(anime)
                session.commit()
                return anime.id
            except IntegrityError as e:
                print(f'Error: {e.args[0]}')

    def _crerate_dto_tag(self, tag: Tag) -> DTOTag:
        return DTOTag(
            id=tag.id,
            name=tag.name
        )

    def _create_dto_anime(self, anime: Anime) -> DTOAnime:
        return DTOAnime(
            id=anime.id,
            anime_tmdb_id=anime.anime_tmdb_id,
            seasons=anime.seasons,
            watching_season=anime.watching_season,
            last_watched_at=anime.last_watched_at.isoformat() if anime.last_watched_at else None,
            last_watched_episode=anime.last_watched_episode,
            title=anime.title,
            tag=anime.tag.name
        )

    def _init_tags(self):
        with Session(self.engine) as session:
            to_watch = Tag(id=1, name='To Watch')     
            watching = Tag(id=2, name='Watching')
            watched = Tag(id=3, name='Watched')

            tags = session.execute(select(Tag)).fetchall()

            if len(tags) == 0:
                session.add(to_watch)
                session.add(watching)
                session.add(watched)

            session.commit()
