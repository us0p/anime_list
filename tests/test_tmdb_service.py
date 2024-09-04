import asyncio
from unittest import TestCase, IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, Mock, call
from aiohttp import ClientSession
from datetime import datetime

from src.interfaces.movie_service_interface import Genre
from src.products.tmdb import TMDBAnimeDisplayInfo
from src.utils.exceptions import DefaultException
from src.services.tmdb import AnimeInfo, TMDBService

def setup_session_and_response_async_mocks(
        status: int,
        json: dict | None = None,
        url_human_repr: Mock | None = None
) -> tuple[AsyncMock, AsyncMock, AsyncMock]:
    session_mock = AsyncMock(ClientSession)
    response_context_mock = AsyncMock()
    session_mock.get.return_value = response_context_mock
    response_mock = AsyncMock()
    response_mock.status = status
    response_mock.json.return_value = json
    response_mock.url.human_repr = url_human_repr
    response_context_mock.__aenter__.return_value = response_mock

    return session_mock, response_mock, response_context_mock

class TestTMDBServiceInitialization(TestCase):
    def test_api_uri(self):
        api_service = TMDBService("test")
        self.assertEqual(
                api_service._default_uri,
                "https://api.themoviedb.org/3"
        )
        self.assertEqual(
            api_service._default_image_uri,
            "https://image.tmdb.org/t/p/w500"
        )
        self.assertEqual(
            api_service._token,
            "test"
        )

class TestFetch(IsolatedAsyncioTestCase):
    # The order of the events are as follows:
    # 1. A call to session.get() yield an context object.
    # 2. A call to the context.__aenter__() method yield the response 
    #    object (this part is all done in the async with 
    #    session.get(...) as response).
    #    An async context object is defined by the pair of awaitable
    #    dunder methods __aenter__() and __aexit__().
    #    The return value of __aenter__() is binded to the target 
    #    specified with the "as" clause of the statement (response).
    #    response is then used within the async with block, and is
    #    in this object that we call json().
    # 3. A call to response.json() method produce the future object
    #    which must be awaited and will represent the JSON part of the 
    #    response.
    async def test_can_receive_query_params(self):
        session_mock = setup_session_and_response_async_mocks(
            200,
        )[0]

        api_service = TMDBService("test")
        await api_service._fetch(
            session_mock,
            "https://template-url.com",
            params={"test": 123}
        )

        session_mock.get.assert_called_with(
            'https://template-url.com',
            params = {"test": 123}
        )

    async def test_raises_error_for_status(self):
        session_mock = setup_session_and_response_async_mocks(
            400,
            {"status_message": "failed"},
            Mock(return_value="https://test.com")
        )[0]

        api_service = TMDBService("test")
        try:
            await api_service._fetch(
                session_mock,
                "https://template-url.com"
            )
            raise Exception("Should have failed with default exception")
        except DefaultException as e:
            self.assertIs(e.args[0], "failed")
            self.assertEqual(e.context["status"], 400)
            self.assertIs(e.context["url"], "https://test.com")
            self.assertIsNone(e.context["req_body"])
            self.assertEqual(
                e.context["res_body"],
                {"status_message": "failed"}
            )

    async def test_return_json_as_dict(self):
        session_mock, response_mock = setup_session_and_response_async_mocks(
            200,
            {"ok": "success"}
        )[0:2]

        api_service = TMDBService("test")

        result = await api_service._fetch(
            session_mock,
            "https://template-url.com"
        )

        response_mock.json.assert_awaited()
        self.assertEqual(
            result,
            {"ok": "success"}
        )

class TestTMDBServiceGetAimeSeriesList(IsolatedAsyncioTestCase):
    async def test_get_anime_series_necessary_query_params(self):
        session_mock = setup_session_and_response_async_mocks(
            200
        )[0]

        api_service = TMDBService("test")
        await api_service._fetch_animes(
            session_mock,
            1,
            "19,17,18"
        )
        session_mock.headers.__setitem__.assert_called_with(
            "Authorization", 
            'Bearer test'
        )
        session_mock.get.assert_called_with(
            'https://api.themoviedb.org/3/discover/tv',
            params = {
                "include_adult": "false",
                "include_null_first_air_dates": "false",
                "page": 1,
                "sort_by": "popularity.desc",
                "with_genres": "16,19,17,18",
                "with_origin_country": "JP"
            }
        )

class TestAsyncParseAnimeSeriesList(TestCase):
    def test_parse_anime_series_list(self):
        anime_list_mock: list[AnimeInfo] = [{
            'adult': False,
            'backdrop_path': '/p0dpg6vwRbGIoWB7hS7AqcqAkYi.jpg',
            'genre_ids': [10759, 16, 9648, 10765],
            'id': 34141,
            'origin_country': ['JP'],
            'original_language': 'ja',
            'original_name': 'D.Gray-man',
            'overview': 'nice overview',
            'popularity': 577.235,
            'poster_path': '/txCtE7ToSLuG8sy8tAIh9q5JAYS.jpg',
            'first_air_date': '2006-10-03',
            'name': 'D.Gray-man',
            'vote_average': 8.117,
            'vote_count': 141
        }]

        genres_list_mock: list[Genre] = [{"id": 16, "name": "Animation"}]

        api_service = TMDBService("test")
        parsed_anime_list = api_service._parse_fetched_animes(
            anime_list_mock,
            genres_list_mock
        )

        self.assertDictEqual(
            parsed_anime_list[0],
            TMDBAnimeDisplayInfo(
                anime_list_mock[0]["id"],
                anime_list_mock[0]["name"],
                anime_list_mock[0]["overview"],
                ["Animation"],
                anime_list_mock[0]["first_air_date"],
                f"{api_service._default_image_uri}{anime_list_mock[0]['poster_path']}"
            ).__dict__
        )

class TestDefaultRequestErrorHandler(TestCase):
    def test_raise_default_error_with_context_info_for_error_status(self):
        api_service = TMDBService('test')
        response = Mock()
        response.status = 400
        response.url.human_repr.return_value="https://test.com"
        req_body = None
        res_body = {"status_message": "failed"}
        try:
            api_service._raise_for_status(response, req_body, res_body)
        except DefaultException as e:
            self.assertIs(e.args[0], "failed")
            self.assertEqual(e.context["status"], 400)
            self.assertIs(e.context["url"], "https://test.com")
            self.assertIsNone(e.context["req_body"])
            self.assertEqual(
                e.context["res_body"],
                {"status_message": "failed"}
            )

    def test_does_not_raise_error_for_success_status(self):
        api_service = TMDBService('test')
        response = Mock()
        response.status = 200
        response.url.human_repr.return_value="https://test.com"
        req_body = None
        res_body = {}
        api_service._raise_for_status(response, req_body, res_body)

class TestGenreFilterConversion(TestCase):
    def test_empty_filter(self):
        genres = []
        filter = ""
        service = TMDBService("test")
        converted_filter = service._convert_genre_filter(genres, filter)
        self.assertEqual(converted_filter, "")

    def test_remove_animation_filter(self):
        genres = []
        filter = "Animation"
        service = TMDBService("test")
        converted_filter = service._convert_genre_filter(genres, filter)
        self.assertEqual(converted_filter, "")

    def test_genre_filter_conversion(self):
        genres: list[Genre] = [
            {"id": 18, "name": "TEST1"},
            {"id": 19, "name": "TEST2"},
            {"id": 20, "name": "TEST3"}
        ]
        filter = "test1, TEST2"
        service = TMDBService("test")
        converted_filter = service._convert_genre_filter(genres, filter)
        self.assertEqual(converted_filter, "18,19")

class TestFetchAnimesByName(IsolatedAsyncioTestCase):
    async def test__fetch_anime_by_name(self):
        mock_response = {
            "page": 1,
            "results": [],
            "total_pages": 1,
            "total_results": 0
        }
 
        session_mock = setup_session_and_response_async_mocks(
            200,
            mock_response
        )[0]

        service = TMDBService("test")
        response = await service._fetch_anime_by_name(
            session_mock,
            1,
            "test"
        )

        session_mock.headers.__setitem__.assert_called_with(
            "Authorization", 
            'Bearer test'
        )
        session_mock.get.assert_called_with(
            f"{service._default_uri}/search/tv",
            params={
                "include_adult": "false",
                "page": 1,
                "language": "en-US",
                "query": "test"
            }
        )
        self.assertEqual(response, mock_response)

    async def test__fetch_anime_by_name_pagination(self):
        session_mock = setup_session_and_response_async_mocks(
            200
        )[0]

        service = TMDBService("test")
        await service._fetch_anime_by_name(
            session_mock,
            2,
            "test"
        )

        session_mock.get.assert_called_with(
            f"{service._default_uri}/search/tv",
            params={
                "include_adult": "false",
                "page": 2,
                "language": "en-US",
                "query": "test"
            }
        )

class TestGetAnimeList(IsolatedAsyncioTestCase):
    async def test_anime_list(self):
        session_mock = AsyncMock(ClientSession)
        api_service = TMDBService('test')
        api_service._fetch_animes = AsyncMock()
        api_service._fetch_animes.return_value = {
            "page": 1,
            "results": [],
            "total_pages": 0
        }

        genres = [{"id": 16, "name": "Animation"}]
        api_service.get_genres_list = AsyncMock()
        api_service.get_genres_list.return_value = genres  

        api_service._parse_fetched_animes = Mock()
        api_service._parse_fetched_animes.return_value = []
        api_service._convert_genre_filter = Mock()
        api_service._convert_genre_filter.return_value = ""

        page = 1
        genres_filter = ""

        anime_list_return = await api_service.get_anime_list(
            session_mock,
            page,
            genres_filter
        )
        self.assertEqual(anime_list_return["anime_list"], [])
        self.assertEqual(anime_list_return["page"], 1)
        self.assertEqual(anime_list_return["total_pages"], 0)
        api_service.get_genres_list.assert_awaited()
        api_service._fetch_animes.assert_awaited()
        api_service._fetch_animes.assert_called_with(
            session_mock,
            page,
            genres_filter
        )
        api_service._convert_genre_filter.assert_called_with(
            genres,
            genres_filter
        )
        api_service._parse_fetched_animes.assert_called_with(
            [],
            genres
        )

class TestFetchAnimeDetails(IsolatedAsyncioTestCase):
    results = [
        {
            "id": 1,
            "name": "test",
            "overview": "explanatory text",
            "genres": [{"id": 1, "name": "Animation"}],
            "first_air_date": "2024-08-28",
            "poster_path": "/something",
            "number_of_episodes": 1014,
            "number_of_seasons": 22,
            "status": "airing",
        },
        {
            "results": [
                {"key": "asdf", "name": "video name", "site": "YouTube"},
                {"key": "fdsa", "name": "video name 2", "site": "X"},
            ]
        }
    ]

    async def test_calls_detail_and_video_endpoint_concurrently(self):
        session_mock, response_mock, response_context_mock = setup_session_and_response_async_mocks(
            200,
        )
        called_at: list[datetime] = []

        async def mock_concurrent_get():
            called_at.append(datetime.now())
            await asyncio.sleep(1)
            return response_mock

        i = 0
        async def mock_different_responses():
            nonlocal i
            result = self.results[i]
            i += 1
            return result

        response_context_mock.__aenter__.side_effect = mock_concurrent_get
        response_mock.json.side_effect = mock_different_responses

        api_service = TMDBService("test")
        await api_service.get_anime_details(session_mock, api_id=123)

        coro1_called_at, coro2_called_at = called_at
        self.assertEqual(
            coro1_called_at.second,
            coro2_called_at.second,
            msg="Calls weren't made at the same time, execution is not concurrent"
        )

    async def test_fetch_anime_details(self):
        session_mock, response_mock = setup_session_and_response_async_mocks(
            200
        )[0:2]

        i = 0
        async def mock_different_respones():
            nonlocal i
            result = self.results[i]
            i += 1
            return result

        response_mock.json.side_effect = mock_different_respones

        api_service = TMDBService('test')
        anime_details = await api_service.get_anime_details(
                session_mock,
                api_id=123
        )
        self.assertEqual(session_mock.get.call_count, 2)
        session_mock.get.assert_has_calls([
            call("https://api.themoviedb.org/3/tv/123", params=None),
            call("https://api.themoviedb.org/3/tv/123/videos", params=None)
        ], any_order=True)

        details = self.results[0]
        self.assertEqual(anime_details["api_id"], details["id"])
        self.assertEqual(anime_details["title"], details["name"])
        self.assertEqual(anime_details["overview"], details["overview"])
        self.assertEqual(anime_details["genres"], ["Animation"])
        self.assertEqual(anime_details["release_date"], '2024-08-28')
        self.assertEqual(
            anime_details["cover_url"],
            f"{api_service._default_image_uri}/something"
        )
        self.assertEqual(anime_details["episodes_count"], 1014)
        self.assertEqual(anime_details["seasons_count"], 22)
        self.assertEqual(anime_details["status"], 'airing')
        self.assertEqual(
            anime_details["trailers"],
            [{
                "name": "video name",
                "link": "https://www.youtube.com/watch?v=asdf",
                "site": "YouTube"
            }]
        )

class TestGetGenresList(IsolatedAsyncioTestCase):
    async def test_get_genres_list(self):
        session_mock = setup_session_and_response_async_mocks(
            200,
            {"genres": [{"id": 16, "name": "Animation"}]}
        )[0]

        service = TMDBService("test")
        genres = await service.get_genres_list(session_mock)
        session_mock.headers.__setitem__.assert_called_with(
            "Authorization", 
            'Bearer test'
        )
        self.assertIs(type(genres), list)
        self.assertEqual(
            genres[0],
            {"id": 16, "name": "Animation"}
        )

class TestGetAnimeListByName(IsolatedAsyncioTestCase):
    async def test_get_anime_list_by_name(self):
        session_mock = setup_session_and_response_async_mocks(
            200
        )[0]

        service = TMDBService('test')
        service._fetch_anime_by_name = AsyncMock()
        service._fetch_anime_by_name.return_value = {
            "page": 1,
            "results": [],
            "total_pages": 1,
            "total_results": 0
        }
        service._parse_fetched_animes = Mock()
        service._parse_fetched_animes.return_value = []
        service.get_genres_list = AsyncMock()
        service.get_genres_list.return_value = []

        query_name = 'dragon'
        page = 1
        genres_filter = ""

        anime_list = await service.get_anime_list_by_name(
            session_mock,
            query_name,
            page,
            genres_filter
        )

        service.get_genres_list.assert_called_with(
            session_mock
        )

        service._fetch_anime_by_name.assert_called_with(
            session_mock,
            page,
            query_name
        )

        service._parse_fetched_animes.assert_called_with(
            [],
            []
        )
        self.assertEqual(
            anime_list,
            {"total_pages": 1, "anime_list": [], "page": 1}
        )

    async def test_get_anime_list_by_name_genre_filter(self):
        session_mock = setup_session_and_response_async_mocks(
            200
        )[0]

        fetch_result_mock = [
            {
                'genre_ids': [17],
                'origin_country': ['JP'],
            },
            {
                'genre_ids': [17],
                'origin_country': ['US'],
            },
            {
                'genre_ids': [16,17,18],
                'origin_country': ['JP'],
            }
        ]

        service = TMDBService("test")
        service._fetch_anime_by_name = AsyncMock()
        service._fetch_anime_by_name.return_value = {
            "page": 1,
            "results": fetch_result_mock,
            "total_pages": 1,
            "total_results": 1
        }

        genres: list[Genre] = [
            {"id": 16, "name": "Animation"},
            {"id": 17, "name": "Horror"},
            {"id": 18, "name": "Fiction"}
        ]

        service.get_genres_list = AsyncMock()
        service.get_genres_list.return_value = genres
        service._parse_fetched_animes = Mock()
        service._parse_fetched_animes.return_value = []
        service._convert_genre_filter = Mock()
        service._convert_genre_filter.return_value = "17,18"

        anime_name = 'test'
        page = 1
        genres_filter = "Animation, horror,Fiction"

        await service.get_anime_list_by_name(
            session_mock,
            anime_name,
            page,
            genres_filter
        )

        service._convert_genre_filter.assert_called_with(
            genres,
            genres_filter
        )

        service._parse_fetched_animes.assert_called_with(
            [fetch_result_mock[2]],
            genres
        )
