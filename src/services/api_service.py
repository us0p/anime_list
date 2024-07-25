from typing import TypedDict
from aiohttp import ClientSession

from ..interfaces.anime_display_info import TMDBAnimeDisplayInfo
from ..interfaces.default_error_interface import IDefaultException

AnimeInfo = TypedDict(
    "AnimeInfo",
    {
      "adult": bool,
      "backdrop_path": str,
      "genre_ids": list[int],
      "id": int,
      "origin_country": list[str],
      "original_language": str,
      "original_name": str,
      "overview": str,
      "popularity": float,
      "poster_path": str,
      "first_air_date": str, # yyyy-mm-dd
      "name": str,
      "vote_average": float,
      "vote_count": int
    }
)

class ApiService():
    default_uri = "https://api.themoviedb.org/3"
    default_image_uri = "https://image.tmdb.org/t/p/w500"
    token = ""

    def __init__(self, token: str):
        self.token = token

    async def get_anime_series_list(
            self,
            session: ClientSession,
            page = 1,
    ):
        session.headers["Authorization"] = f'Bearer {self.token}'
        params = {
            "include_adult": "false",
            "include_null_first_air_dates": "false",
            "page": page,
            "sort_by": "popularity.desc",
            "with_genres": 16, # Animation
            "with_original_language": "ja"
        }
        async with session.get(
            f'{self.default_uri}/discover/tv',
            params=params
        ) as response:
                resp_body = await response.json()
                if response.status >= 400:
                    raise IDefaultException(
                        resp_body["status_message"],
                        {
                            "status": response.status,
                            "url": response.url.human_repr(),
                            "req_body": None,
                            "res_body": resp_body,
                        }
                    )

                return resp_body

    async def parse_get_anime_series_list(
            self,
            anime_list: list[AnimeInfo],
            session: ClientSession
    ) -> list[TMDBAnimeDisplayInfo]:
            session.headers["Authorization"] = f"Bearer {self.token}"
            async with session.get(
                f'{self.default_uri}/genre/tv/list?language=en'
            ) as response:
                result = await response.json()
                if response.status >= 400:
                    raise IDefaultException(
                        result["status_message"],
                        {
                            "status": response.status,
                            "url": response.url.human_repr(),
                            "req_body": None,
                            "res_body": result
                        }
                    )
                genres = result["genres"]
                parsed_anime_list = []
                for anime in anime_list:
                     parsed_anime_list.append(TMDBAnimeDisplayInfo(
                        anime["id"],
                        anime["name"],
                        anime["overview"],
                        [g["name"] for g in genres if g["id"] in anime["genre_ids"]],
                        anime["first_air_date"],
                        anime["poster_path"]
                    ))

                return parsed_anime_list
