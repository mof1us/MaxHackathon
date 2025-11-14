class UniversityEntity:
    id: int
    name: str

    def __init__(self, id: int=0, name: str="undefined") -> None:
        self.id = id
        self.name = name

    def __str__(self):
        return str(self.id) + " - " + self.name

    def json(self) -> dict:
        return {"id": self.id, "name": self.name}
