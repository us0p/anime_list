from ..interfaces.displayer_interface import AnimeDetailedInfo, AnimeListItem, Trailer

class TMDBAnimeDisplayInfo():
    api_id: int
    title: str
    overview: str
    genres: list[str]
    release_date: str
    cover_url: str

    def __init__(
        self, 
        api_id: int,
        title: str,
        overview: str,
        genres: list[str],
        release_date: str,
        cover_url: str
    ):
        self.api_id = api_id
        self.title = title
        self.overview = overview
        self.genres = genres
        self.release_date = release_date
        self.cover_url = cover_url

    def get_dict(self) -> AnimeListItem:
        return {
            "api_id": self.api_id,
            "title": self.title,
            "overview": self.overview,
            "genres": self.genres,
            "cover_url": self.cover_url,
            "release_date": self.release_date
        }

class TMDBAnimeDetailDisplayInfo(TMDBAnimeDisplayInfo):
    episodes_count: int
    sesons_count: int
    status: str
    trailers: list[Trailer]

    def __init__(
        self,
        api_id: int,
        title: str,
        overview: str,
        genres: list[str],
        release_date: str,
        cover_url: str,
        episodes_count: int,
        seasons_count: int,
        status: str,
        trailers: list[Trailer]
    ):
        super().__init__(
            api_id,
            title,
            overview,
            genres,
            release_date,
            cover_url,
        )
        self.episodes_count = episodes_count
        self.seasons_count = seasons_count
        self.status = status
        self.trailers = trailers

    def get_dict(self) -> AnimeDetailedInfo:
        d = super().get_dict()
        return {
            **d,
            "status": self.status,
            "trailers": self.trailers,
            "seasons_count": self.seasons_count,
            "episodes_count": self.episodes_count
        }
