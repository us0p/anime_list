from unittest import TestCase, IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, Mock
from aiohttp import ClientResponse, ClientSession

from src.interfaces.anime_display_info import TMDBAnimeDisplayInfo
from src.interfaces.default_error_interface import IDefaultException
from src.services.api_service import AnimeInfo, ApiService

class TestApiServiceInitialization(TestCase):
    def test_api_uri(self):
        api_service = ApiService("test")
        self.assertEqual(
                api_service.default_uri,
                "https://api.themoviedb.org/3"
        )
        self.assertEqual(
            api_service.default_image_uri,
            "https://image.tmdb.org/t/p/w500"
        )
        self.assertEqual(
            api_service.token,
            "test"
        )


class TestApiServiceGetAimeSeriesList(IsolatedAsyncioTestCase):
    async def test_get_anime_series(self):
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
        #    in this object that whe call json().
        # 3. A call to response.json() method produce the future object
        #    which must be awaited and will represent the JSON part of the 
        #    response.

        session_mock = AsyncMock(ClientSession)
        response_context_mock = AsyncMock()
        session_mock.get.return_value = response_context_mock
        response_mock = AsyncMock()
        response_mock.status = 200
        response_context_mock.__aenter__.return_value = response_mock

        api_service = ApiService("test")
        await api_service.get_anime_series_list(
            session_mock
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
                "with_genres": 16,
                "with_original_language": "ja"
            }
        )
        response_mock.json.assert_awaited()

    async def test_get_anime_series_list_with_page_argument(self):
        session_mock = AsyncMock(ClientSession)
        response_context_mock = AsyncMock()
        session_mock.get.return_value = response_context_mock
        response_mock = AsyncMock()
        response_mock.status = 200
        response_context_mock.__aenter__.return_value = response_mock

        api_service = ApiService("test")
        await api_service.get_anime_series_list(
            session_mock,
            10
        )

        session_mock.get.assert_called_with(
            'https://api.themoviedb.org/3/discover/tv',
            params = {
                "include_adult": "false",
                "include_null_first_air_dates": "false",
                "page": 10,
                "sort_by": "popularity.desc",
                "with_genres": 16,
                "with_original_language": "ja"
            }
        )

    async def test_get_anime_series_list_raises_default_error(self):
        session_mock = AsyncMock(ClientSession)
        response_context_mock = AsyncMock()
        session_mock.get.return_value = response_context_mock
        response_mock = AsyncMock(ClientResponse)
        response_mock.status = 400
        response_mock.json.return_value = {"status_message": "failed"}
        response_mock.url.human_repr = Mock(return_value="https://test.com")
        response_context_mock.__aenter__.return_value = response_mock

        api_service = ApiService("test")
        try:
            await api_service.get_anime_series_list(
                session_mock
            )
            raise Exception("Should have failed with default exception")
        except IDefaultException as e:
            self.assertIs(e.args[0], "failed")
            self.assertEqual(e.context["status"], 400)
            self.assertIs(e.context["url"], "https://test.com")
            self.assertIsNone(e.context["req_body"])
            self.assertEqual(
                e.context["res_body"],
                {"status_message": "failed"}
            )

class TestAsyncParseAnimeSeriesList(IsolatedAsyncioTestCase):
    async def test_parse_anime_series_list(self):
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

        genres_list_mock = {
            "genres": [{
                "id": 16,
                "name": "Animation"
            }]
        }

        session_mock = AsyncMock(ClientSession)
        response_context_mock = AsyncMock()
        session_mock.get.return_value = response_context_mock
        response_mock = AsyncMock()
        response_mock.status = 200
        response_mock.url.human_repr = Mock(return_value="https://test.com")
        response_mock.json.return_value = genres_list_mock
        response_context_mock.__aenter__.return_value = response_mock

        api_service = ApiService("test")
        parsed_anime_list = await api_service.parse_get_anime_series_list(
            anime_list_mock,
            session_mock
        )

        session_mock.headers.__setitem__.assert_called_with(
            "Authorization", 
            'Bearer test'
        )
        session_mock.get.assert_called_with(
            f'{api_service.default_uri}/genre/tv/list?language=en'
        )
        response_mock.json.assert_awaited()
        self.assertDictEqual(
            parsed_anime_list[0].__dict__,
            TMDBAnimeDisplayInfo(
                anime_list_mock[0]["id"],
                anime_list_mock[0]["name"],
                anime_list_mock[0]["overview"],
                ["Animation"],
                anime_list_mock[0]["first_air_date"],
                anime_list_mock[0]["poster_path"]
            ).__dict__
        )

    async def test_parse_anime_series_list_error(self):
        session_mock = AsyncMock(ClientSession)
        response_context_mock = AsyncMock()
        session_mock.get.return_value = response_context_mock
        response_mock = AsyncMock()
        response_mock.status = 400
        response_mock.url.human_repr = Mock(return_value="https://test.com")
        response_mock.json.return_value = {"status_message": "failed"}
        response_context_mock.__aenter__.return_value = response_mock

        api_service = ApiService("test")
        try:
            await api_service.parse_get_anime_series_list(
                [],
                session_mock
            )
            raise Exception("Should have failed with default error")
        except IDefaultException as e:
            self.assertIs(e.args[0], "failed")
            self.assertEqual(e.context["status"], 400)
            self.assertIs(e.context["url"], "https://test.com")
            self.assertIsNone(e.context["req_body"])
            self.assertEqual(
                e.context["res_body"],
                {"status_message": "failed"}
            )
