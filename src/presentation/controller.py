import asyncio
from aiohttp import ClientSession

from ..presentation.anime_info_displayers import AnimeDetailedItemDisplayer, AnimeListItemDisplayer, ListDisplayer

from ..presentation.image_builder import ImageBuilder

from ..utils.exceptions import DefaultException
from ..interfaces.movie_service_interface import IService

class Controller:
    service: IService
    image_builder: ImageBuilder

    def __init__(self, service: IService):
        self.service = service
        self.image_builder = ImageBuilder()

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
