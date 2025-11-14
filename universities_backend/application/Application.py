from fastapi import FastAPI

from database.entities.UniversityEntity import UniversityEntity
from database.services.UniversityService import UniversitiesService


class Application:
    def __init__(self):
        self.app = FastAPI()
        self.uni_service = UniversitiesService()
        self.__register_endpoints()


    def __register_endpoints(self):
        @self.app.get("/universities")
        def get_universities(query: str):
            return list(map(lambda x: x.json(), self.uni_service.find_uni(query)))

        @self.app.post("/universities")
        def create_university(name: str):
            check_uni = self.uni_service.get_uni_by_name(name)
            if check_uni is not None:
                return {"id": check_uni.id}
            return {"id": self.uni_service.create_uni(UniversityEntity(name=name))}
