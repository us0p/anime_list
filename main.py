import asyncio
import os
from typing import List, Optional
from dotenv import load_dotenv
from src.services.tmdb import TMDBService
from src.presentation.cli_parser import DefaultArgumentParser

from src.presentation.controller import Controller

from sqlalchemy import ForeignKey, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session
from sqlalchemy.orm import mapped_column, relationship

from datetime import datetime

class Base(DeclarativeBase):
    pass

class Tag(Base):
    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)

    users: Mapped[List["Anime"]] = relationship(back_populates="tag")

class Anime(Base):
    __tablename__ = "anime"

    id: Mapped[int] = mapped_column(primary_key=True)
    anime_tmdb_id: Mapped[int] = mapped_column(nullable=False, unique=True)
    seasons: Mapped[int] = mapped_column(nullable=False)
    watching_season: Mapped[Optional[int]]
    las_watched_episode: Mapped[Optional[int]]
    last_watched_at: Mapped[Optional[datetime]]
    title: Mapped[str] = mapped_column(nullable=False)
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tag.id"),
        nullable=False
    )

    tag: Mapped[Tag] = relationship(back_populates="users")

if __name__ == "__main__":
    engine = create_engine("sqlite+pysqlite:///test.db", echo=True)

    Base.metadata.create_all(engine)

    # Session gets a new connection from the engine each time it needs
    # to execute SQL against the database.
    with Session(engine) as session:
        #session.execute(text("""
        #CREATE TABLE test (x int, y text, z real);
        #"""))
        #session.execute(
        #    text("INSERT INTO tag (name) VALUES (:name);"),
        #    [
        #        {"name": "To watch"},
        #        {"name": "Watching"},
        #        {"name": "Watched"}
        #    ]
        #)
        # session.execute return a row object which is a tuple of the table
        # columns, or in the case of ORM select, it's a tuple with an
        # instance of the Table as the first element.
        # scalars return a list of rows but it returns the first value of
        # the row, thus, it's commonly used with ORM selects to get the
        # instance for each row instead of a tuple.
        # if you select specific columns, the Return object rows will be
        # a tuple with each element representing the specified row, it won't
        # be a instance of the class.
        result = session.scalars(select(Tag))
        for row in result:
            print(row.id, row.name)

        #session.commit()

    #load_dotenv()
    #default_argparse = DefaultArgumentParser()
    #namespace = default_argparse.parse()
    #tmdb_service = TMDBService(str(os.getenv("TMDB_API_TOKEN")))
    #controller = Controller(tmdb_service)
    #match namespace.command:
    #    case 'search':
    #        if namespace.id:
    #            asyncio.run(
    #                controller.service_get_anime_details(
    #                    namespace.id
    #                )
    #            )
    #        elif namespace.name:
    #            asyncio.run(
    #                controller.service_list_animes_by_name(
    #                    namespace.name,
    #                    namespace.page,
    #                    namespace.genres
    #                )
    #            )
    #        else:
    #            asyncio.run(
    #                controller.service_list_animes(
    #                    namespace.page,
    #                    namespace.genres
    #                )
    #            )
    #    case "genres":
    #        asyncio.run(controller.service_get_genres())
    #    case _:
    #        print("Command doesn't exist")
