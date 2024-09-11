from datetime import datetime
from typing import Optional
from sqlalchemy import Engine, create_engine, select
from sqlalchemy.orm import Session

from ..models.anime import Anime
from ..models.base import Base
from ..models.tag import Tag

class MetaDB(type):
    instances_ = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls.instances_:
            cls.instances_[cls] = super().__call__(*args, **kwargs)
        return cls.instances_[cls]
        
class Database(metaclass=MetaDB):
    engine: Engine
    def __init__(self):
        self.engine = create_engine(
            "sqlite+pysqlite:///test.db",
            echo=False
        )
        Base.metadata.create_all(self.engine)

    def select_all_tags(self):
        with Session(self.engine) as session:
            tags = session.execute(select(Tag)).scalars().fetchall()
            return tags

    def insert_anime(
        self,
        anime_tmdb_id: int,
        seasons: int,
        watching_season: Optional[int],
        last_watched_episode: Optional[int],
        last_watched_at: Optional[datetime],
        title: str,
        tag_id: int
    ):
        with Session(self.engine) as session:
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
