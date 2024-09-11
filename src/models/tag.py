from .base import Base
from .anime import Anime

from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship

class Tag(Base):
    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)

    users: Mapped[List["Anime"]] = relationship(back_populates="tag")
