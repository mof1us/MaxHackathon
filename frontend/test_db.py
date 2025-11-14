from database.entities.UserMenuEntity import UserMenuEntity
from database.services.UserService import UserService


if __name__ == "__main__":
    service = UserService()
    # service.create_user(UserMenuEntity(
    #     id=4,
    #     metadata={"id": 2, "bb": "123124124e"},
    #     position="test"
    # ))"title": "asdasd"
    # service.create_user(UserMenuEntity(
    #     id=5,
    #     metadata={"id": 2, "bb": "123124124e"},
    #     position="test"
    # ))
    # service.change_user(UserMenuEntity(5, "testedited2", {"id": "changed"}))
    # print(service.get_user(5).position)
    # service.change_user(UserMenuEntity(5, "testedited", {"id": "changed"}))
    # print(service.get_user(5).position)
    