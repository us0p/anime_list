import asyncio
import os
from aiohttp import ClientSession
from dotenv import load_dotenv
from src.services.display_service import DisplayService
from src.interfaces.default_error_interface import IDefaultException
from src.services.api_service import ApiService
from src.parsers.default_parser import DefaultArgumentParser

if __name__ == "__main__":
    load_dotenv()
    display_service = DisplayService()
    display_service.read_image_from_url()

    #default_argparse = DefaultArgumentParser()
    #namespace = default_argparse.parse()
    #api_service = ApiService(str(os.getenv("TMDB_API_TOKEN")))
    #async def a ():
    #    async with ClientSession() as session:
    #        try:
    #            a = await api_service.get_anime_series_list(session)
    #            anime_list = await api_service.parse_get_anime_series_list(
    #                a["results"],
    #                session
    #            )
    #            for anime in anime_list:
    #                print('-' * 75)
    #                print(f"ID: {anime.api_id}")
    #                print(f"Name: {anime.title}")
    #                print(f"Overview: {anime.overview}")
    #                print(f"Genres: {anime.genres}")
    #                print(f"Release date: {anime.release_date}")
    #        except IDefaultException as e:
    #            print(f"Error: {e}")

    #asyncio.run(a())
