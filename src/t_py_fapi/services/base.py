class BaseService:
    """Marker base for services.

    Deliberately stateless: repositories own the session, services own the
    entity-to-DTO mapping. A service that needs the session directly is
    reaching across into the repository layer.
    """
