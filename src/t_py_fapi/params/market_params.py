from datetime import datetime, time

from pydantic import BaseModel, PrivateAttr
from sqlalchemy import and_, not_, or_
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.sql.elements import ColumnElement

from t_py_fapi.database import Market, Street


class GetMarketParams(BaseModel):
    """Query parameters for GET /markets.

    Future pagination/sorting models (GetAllPaged, GetAllSorted) belong beside
    this one in params/, composed by per-entity children such as MarketSorted.
    """

    street_id: int | None = None
    city_id: int | None = None
    is_open: bool | None = None

    # Private: query parsing never sees it, and every instance stamps a fresh
    # clock. Tests pin it directly instead (params._selected_time = ...).
    _selected_time: time = PrivateAttr(default_factory=lambda: datetime.now().time())

    def joins(self) -> list[InstrumentedAttribute]:
        """Relationships that must be joined before conditions() apply."""
        return [Market.street] if self.city_id is not None else []

    def conditions(self) -> list[ColumnElement[bool]]:
        """Clauses for Select.where(): one per set field, ANDed by the caller."""
        clauses: list[ColumnElement[bool]] = []
        if self.street_id is not None:
            clauses.append(Market.street_id == self.street_id)
        if self.city_id is not None:
            clauses.append(Street.city_id == self.city_id)
        if self.is_open is not None:
            # A window that wraps past midnight (closing <= opening) is open on
            # either side of it, hence the second branch. Boundaries are
            # inclusive.
            now = self._selected_time
            within = or_(
                and_(Market.opening_time <= now, Market.closing_time >= now),
                and_(
                    Market.opening_time > Market.closing_time,
                    or_(Market.opening_time <= now, Market.closing_time >= now),
                ),
            )
            clauses.append(within if self.is_open else not_(within))
        return clauses
