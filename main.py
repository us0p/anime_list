import asyncio
import os
from dotenv import load_dotenv
from src.services.tmdb import TMDBService
from src.presentation.cli_parser import DefaultArgumentParser

from src.presentation.controller import Controller

if __name__ == "__main__":
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
            else:
                asyncio.run(
                    controller.service_list_animes(namespace.page)
                )
        case "genres":
            asyncio.run(controller.service_get_genres())
        case _:
            print("Command doesn't exist")
