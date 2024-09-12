import asyncio
from datetime import date
from typing import Optional
from aiohttp import ClientSession

from ..interfaces.database_interface import IDatabase

from ..presentation.anime_info_displayers import AnimeDetailedItemDisplayer, AnimeListItemDisplayer, DBAnimeDisplayer, ListDisplayer

from ..presentation.image_builder import ImageBuilder

from ..utils.exceptions import DefaultException
from ..interfaces.movie_service_interface import IService

class Controller:
    service: IService
    image_builder: ImageBuilder
    db: IDatabase

    def __init__(self, service: IService, db: IDatabase):
        self.service = service
        self.image_builder = ImageBuilder()
        self.db = db

    def db_get_anime(self, anime_id: int):
        anime = self.db.get_anime_by_id(anime_id)
        
        if anime == None:
            print(f"Anime ID: {anime_id} doesn't exist.")
            return

        d = DBAnimeDisplayer([anime])
        d.render_info()

    def db_list_animes(self, name: Optional[str]):
        animes = []
        if name:
            animes = self.db.select_animes_by_title(name)
        else:
            animes = self.db.get_animes()
        d = DBAnimeDisplayer(animes)
        d.render_info()

    def db_list_tags(self):
        tags = self.db.select_all_tags()
        d = ListDisplayer(
            "Tags",
            [f"id: {t.id}, name: {t.name}" for t in tags]
        )
        d.render_info()

    def db_delete_anime(self, anime_id: int):
        anime = self.db.delete_anime(anime_id)
        if anime:
            print(f"Anime: {anime.title} deleted.")
            return
        print(f"Anime ID: {anime_id} doesn't exist.")

    def db_update_anime(
        self,
        anime_id: int,
        last_season: Optional[int],
        last_episode: Optional[int],
        new_tag: Optional[int]
    ):
        anime = self.db.update_anime(
            anime_id,
            last_season,
            last_episode,
            new_tag
        )
        if anime:
            print(f"Anime: {anime.title} updated.")
            return
        print(f"Anime ID: {anime_id} doesn't exist.")
        pass

    async def sdb_create_anime(
        self,
        anime_id: int,
        tag_id: int,
        watching_season: Optional[int],
        last_watched_episode: Optional[int],
        last_watched_at: Optional[str]
    ):
        async with ClientSession() as session:
            try:
                db_anime = self.db.get_anime_by_tmdb_id(anime_id)
                if db_anime:
                    print(f"Anime ID: {anime_id} already exists")
                    return 

                anime = await self.service.get_anime_details(
                    session,
                    anime_id
                )

                lwa = date.fromisoformat(
                    last_watched_at
                ) if last_watched_at else None

                anime_dbid = self.db.insert_anime(
                    anime_tmdb_id=anime["api_id"],
                    seasons=anime["seasons_count"],
                    watching_season=watching_season,
                    last_watched_episode=last_watched_episode,
                    last_watched_at=lwa,
                    title=anime["title"],
                    tag_id=tag_id
                )

                print(f'Anime created, id: {anime_dbid}')
            except ValueError as e:
                print(f"Error: {e.args[0]}.")
                print("Date must be in the format YYYY-MM-DD")
            except DefaultException as e:
                print(f'Error: {e}')

    async def service_get_genres(self):
        async with ClientSession() as session:
            try:
                genres = await self.service.get_genres_list(session)
                d = ListDisplayer(
                    "Genres",
                    [genre["name"] for genre in genres]
                )
                d.render_info()
            except DefaultException as e:
                print(f"Error {e}")

    async def service_get_anime_details(self, id: int):
        async with ClientSession() as session:
            try:
                anime_details = await self.service.get_anime_details(
                    session,
                    id
                )
                image = await self.image_builder.produce_ascii_image(
                    session,
                    anime_details["cover_url"]
                )
                d = AnimeDetailedItemDisplayer(
                    anime_details,
                    image
                )
                d.render_info()
            except DefaultException as e:
                print(f"Error {e}")

    async def service_list_animes(self, page: int, genres_filter: str):
        async with ClientSession() as session:
            try:
                anime_list = await self.service.get_anime_list(
                    session,
                    page,
                    genres_filter
                )
                ascii_images_coroutines = [
                    self.image_builder.produce_ascii_image(
                        session,
                        anime["cover_url"]
                    ) for anime in anime_list["anime_list"]
                ]
                
                anime_ascii_images = await asyncio.gather(
                    *ascii_images_coroutines
                )

                print(f'Page: {anime_list["page"]} of {anime_list["total_pages"]}')
                for n in range(len(anime_list["anime_list"])):
                    d = AnimeListItemDisplayer(
                            anime_list["anime_list"][n],
                            anime_ascii_images[n],
                        )
                    d.render_info()
                print(f'Page: {anime_list["page"]} of {anime_list["total_pages"]}')
            except DefaultException as e:
                print(f"Error {e}")

    async def service_list_animes_by_name(
        self,
        name: str,
        page: int,
        genres_filter: str
    ):
        async with ClientSession() as session:
            try:
                anime_list = await self.service.get_anime_list_by_name(
                    session,
                    name,
                    page,
                    genres_filter
                )
                ascii_images_coroutines = [
                    self.image_builder.produce_ascii_image(
                        session,
                        anime["cover_url"]
                    ) for anime in anime_list["anime_list"]
                ]
                
                anime_ascii_images = await asyncio.gather(
                    *ascii_images_coroutines
                )

                print(f'Page: {anime_list["page"]} of {anime_list["total_pages"]}')
                for n in range(len(anime_list["anime_list"])):
                    d = AnimeListItemDisplayer(
                            anime_list["anime_list"][n],
                            anime_ascii_images[n],
                        )
                    d.render_info()
                print(f'Page: {anime_list["page"]} of {anime_list["total_pages"]}')
            except DefaultException as e:
                print(f"Error {e}")
