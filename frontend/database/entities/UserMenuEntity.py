

class UserMenuEntity:
    id: int
    position: str
    metadata: dict

    def __init__(self, id: int, position: str, metadata: dict) -> None:
        self.id = id
        self.metadata = metadata
        self.position = position