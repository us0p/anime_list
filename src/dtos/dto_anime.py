from typing import Optional

class DTOAnime:
    id: int
    anime_tmdb_id: int
    seasons: int
    watching_season: Optional[int]
    last_watched_episode: Optional[int]
    last_watched_at: Optional[str]
    title: str
    tag: str

    def __init__(
        self,
        id: int,
        anime_tmdb_id: int,
        seasons: int,
        watching_season: Optional[int],
        last_watched_episode: Optional[int],
        last_watched_at: Optional[str],
        title: str,
        tag: str
    ):
        self.id = id
        self.anime_tmdb_id = anime_tmdb_id
        self.seasons = seasons
        self.watching_season = watching_season
        self.last_watched_episode = last_watched_episode
        self.last_watched_at  = last_watched_at
        self.title = title
        self.tag = tag
