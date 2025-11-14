from database.entities.UniversityEntity import UniversityEntity
from database.services.UniversityService import UniversitiesService

if __name__ == "__main__":
    service = UniversitiesService()
    # service.create_uni(UniversityEntity(
    #     id=1,
    #     name="НГУ"
    # ))
    # service.create_uni(UniversityEntity(
    #     id=2,
    #     name="СТАНКИН"
    # ))

    for i in service.find_uni("Н"):
        print(i)