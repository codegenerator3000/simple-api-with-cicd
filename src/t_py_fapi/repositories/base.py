from typing import TypeVar

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

# Internal to this module: the repositories type their own statements, so the
# variable needs no name the package could import.
_ModelT = TypeVar("_ModelT")


class BaseRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _all(self, stmt: Select[tuple[_ModelT]]) -> list[_ModelT]:
        """Run a select and return every row as a list of entities.

        Shared so each repository holds only its query, not the scalars-to-list
        ceremony that every read path repeats.
        """
        result = await self.session.scalars(stmt)
        return list(result.all())
