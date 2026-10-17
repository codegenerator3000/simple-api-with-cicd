class StreetNotFoundError(Exception):
    """Raised when a market references a street id that does not exist."""

    def __init__(self, street_id: int) -> None:
        super().__init__(f"street {street_id} does not exist")
        self.street_id = street_id
