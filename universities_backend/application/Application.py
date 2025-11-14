from fastapi import FastAPI

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