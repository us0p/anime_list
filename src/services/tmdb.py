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
        page = 1,
        genres_filter: str = ""
    ) -> AnimeListReturn:
        genres = await self.get_genres_list(session)
        filter = self._convert_genre_filter(genres, genres_filter)

        fetched_animes = await self._fetch_animes(
            session,
            page,
            filter
        )
        anime_list = self._parse_fetched_animes(
            fetched_animes["results"],
            genres
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
        name: str,
        page: int,
        genres_filter: str = ""
    ) -> AnimeListReturn:
        anime_result = await self._fetch_anime_by_name(session, page, name)
        genres = await self.get_genres_list(session)
        filter = self._convert_genre_filter(genres, genres_filter)

        animes = []
        for anime in anime_result["results"]:
            if 16 in anime["genre_ids"]:
                genre_ids = [str(gid) for gid in anime["genre_ids"]]
                if ','.join(genre_ids).find(filter) >= 0:
                    if "JP" in anime["origin_country"]:
                        animes.append(anime)

        anime_list = self._parse_fetched_animes(
            animes,
            genres
        )
        return {
            "total_pages": anime_result["total_pages"],
            "anime_list": anime_list,
            "page": anime_result["page"]
        }

    async def get_genres_list(self, session: ClientSession) -> list[Genre]:
        session.headers["Authorization"] = f'Bearer {self._token}'
        result = await self._fetch(
            session,
            f'{self._default_uri}/genre/tv/list?language=en'
        )
        return result["genres"]

    async def _fetch_anime_by_name(
        self,
        session: ClientSession,
        page: int,
        name: str
    ):
        session.headers["Authorization"] = f'Bearer {self._token}'
        params = {
            "include_adult": "false",
            "page": page,
            "language": "en-US",
            "query": name
        }

        return await self._fetch(
            session,
            f"{self._default_uri}/search/tv",
            params
        )

    async def _fetch_animes(
        self,
        session: ClientSession,
        page: int,
        genres: str = ""
    ):
        session.headers["Authorization"] = f'Bearer {self._token}'
        params = {
            "include_adult": "false",
            "include_null_first_air_dates": "false",
            "page": page,
            "sort_by": "popularity.desc",
            # Animation
            "with_genres": "16" + f",{genres}",
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

    def _parse_fetched_animes(
        self,
        anime_list: list[AnimeInfo],
        genres: list[Genre]
    ) -> list[AnimeListItem]:
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

    def _convert_genre_filter(self, genres: list[Genre], filter: str):
        normalized_filter = filter.strip().lower().split(",")
        filter = ",".join(
            [
                str(g["id"]) 
                for g in genres 
                if g["name"].lower() in normalized_filter
                and g["id"] != 16
            ]
        )
        return filter
