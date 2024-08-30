from asyncio import gather
from typing import TypedDict
from aiohttp import ClientResponse, ClientSession

from ..interfaces.movie_service_interface import AnimeListReturn, Genre, IService

from ..interfaces.displayer_interface import AnimeDetailedInfo, AnimeListItem

from ..products.tmdb import TMDBAnimeDisplayInfo, TMDBAnimeDetailDisplayInfo
from ..utils.exceptions import DefaultException

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

class TMDBService(IService):
    _default_uri = "https://api.themoviedb.org/3"
    _default_image_uri = "https://image.tmdb.org/t/p/w500"
    _default_youtube_uri = "https://www.youtube.com/watch?v="
    _token = ""

    def __init__(self, token: str):
        self._token = token

    async def get_anime_list(
        self,
        session: ClientSession,
        page = 1
    ) -> AnimeListReturn:
        fetched_animes = await self._fetch_animes(session, page)
        anime_list = await self._parse_fetched_animes(
            session,
            fetched_animes["results"]
        )
        return {
            "anime_list": anime_list,
            "page": fetched_animes["page"],
            "total_pages": fetched_animes["total_pages"]
        }

    async def get_anime_details(
        self,
        session: ClientSession,
        api_id: int
    ) -> AnimeDetailedInfo:
        session.headers["Authorization"] = f"Bearer {self._token}"
        details, trailers = await gather(
            self._fetch(
                session,
                f'{self._default_uri}/tv/{api_id}',
            ),
            self._fetch(
                session,
                f'{self._default_uri}/tv/{api_id}/videos'
            )
        )
        anime_details = TMDBAnimeDetailDisplayInfo(
                details["id"],
                details["name"],
                details["overview"],
                [g["name"] for g in details["genres"]],
                details["first_air_date"],
                f'{self._default_image_uri}{details["poster_path"]}',
                details["number_of_episodes"],
                details["number_of_seasons"],
                details["status"],
                [
                    {
                        "link": f'{self._default_youtube_uri}{t["key"]}',
                        "name": t["name"],
                        "site": t["site"]
                    } for t in trailers["results"] 
                    if t["site"] == "YouTube"
                ]
        )
        return anime_details.get_dict()

    async def get_anime_list_by_name(
        self,
        session: ClientSession,
        name: str
    ) -> AnimeListReturn:
        return {"total_pages": 0, "anime_list": [], "page": 0}

    async def get_genres_list(self, session: ClientSession) -> list[Genre]:
        session.headers["Authorization"] = f'Bearer {self._token}'
        result = await self._fetch(
            session,
            f'{self._default_uri}/genre/tv/list?language=en'
        )
        return result["genres"]

    async def _fetch_animes(
        self,
        session: ClientSession,
        page,
    ):
        session.headers["Authorization"] = f'Bearer {self._token}'
        params = {
            "include_adult": "false",
            "include_null_first_air_dates": "false",
            "page": page,
            "sort_by": "popularity.desc",
            "with_genres": 16, # Animation
            "with_origin_country": "JP"
        }
        resp_body = await self._fetch(
            session,
            f'{self._default_uri}/discover/tv',
            params
        )
        return resp_body

    async def _fetch(
        self,
        session: ClientSession,
        url: str,
        params: dict | None = None
    ) -> dict:
        async with session.get(url, params=params) as response:
            result = await response.json()
            self._raise_for_status(response, None, result)
            return result

    async def _parse_fetched_animes(
        self,
        session: ClientSession,
        anime_list: list[AnimeInfo],
    ) -> list[AnimeListItem]:
        session.headers["Authorization"] = f"Bearer {self._token}"
        genres = await self.get_genres_list(session)
        parsed_anime_list: list[AnimeListItem] = []
        for anime in anime_list:
             parsed_anime_list.append(TMDBAnimeDisplayInfo(
                anime["id"],
                anime["name"],
                anime["overview"],
                [g["name"] for g in genres if g["id"] in anime["genre_ids"]],
                anime["first_air_date"],
                f'{self._default_image_uri}{anime["poster_path"]}',
            ).get_dict())

        return parsed_anime_list

    def _raise_for_status(
        self,
        response: ClientResponse,
        req_body: dict | None,
        res_body: dict
    ):
        if response.status >= 400:
            raise DefaultException(
                res_body["status_message"],
                {
                    "status": response.status,
                    "url": response.url.human_repr(),
                    "req_body": req_body,
                    "res_body": res_body
                }
            )
