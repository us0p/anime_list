from .base import Base

from typing import TYPE_CHECKING, Optional
from datetime import date

from sqlalchemy.orm import mapped_column, relationship, Mapped
from sqlalchemy import ForeignKey

if TYPE_CHECKING:
    from .tag import Tag

class Anime(Base):
    __tablename__ = "anime"

    id: Mapped[int] = mapped_column(primary_key=True)
    anime_tmdb_id: Mapped[int] = mapped_column(nullable=False, unique=True)
    seasons: Mapped[int] = mapped_column(nullable=False)
    watching_season: Mapped[Optional[int]]
    last_watched_episode: Mapped[Optional[int]]
    last_watched_at: Mapped[Optional[date]]
    title: Mapped[str] = mapped_column(nullable=False)
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tag.id"),
        nullable=False
    )

    tag: Mapped["Tag"] = relationship(back_populates="users")
