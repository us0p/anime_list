import asyncio
import os
from dotenv import load_dotenv
from src.services.db import Database
from src.services.tmdb import TMDBService
from src.presentation.cli_parser import DefaultArgumentParser

from src.presentation.controller import Controller

if __name__ == "__main__":
    db = Database()
    db._init_tags()

    load_dotenv()
    default_argparse = DefaultArgumentParser()
    namespace = default_argparse.parse()
    tmdb_service = TMDBService(str(os.getenv("TMDB_API_TOKEN")))
    controller = Controller(tmdb_service)
    match namespace.command:
        case 'search':
            if namespace.id:
                asyncio.run(
                    controller.service_get_anime_details(
                        namespace.id
                    )
                )
            elif namespace.name:
                asyncio.run(
                    controller.service_list_animes_by_name(
                        namespace.name,
                        namespace.page,
                        namespace.genres
                    )
                )
            else:
                asyncio.run(
                    controller.service_list_animes(
                        namespace.page,
                        namespace.genres
                    )
                )
        case "genres":
            asyncio.run(controller.service_get_genres())
        case "tags":
            controller.db_list_tags()
        case "add":
            asyncio.run(
                controller.sdb_create_anime(
                    namespace.anime_id,
                    namespace.tag_id,
                    namespace.watching_season,
                    namespace.last_watched_episode,
                    namespace.last_watched_at
                )
            )
        case _:
            print("Command doesn't exist")
