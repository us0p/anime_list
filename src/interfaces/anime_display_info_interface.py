class IAnimeDisplayInfo():
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
