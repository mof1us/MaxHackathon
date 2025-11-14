from database.entities.UserMenuEntity import UserMenuEntity
from psycopg2._psycopg import cursor
from psycopg2.extras import Json

class UserRepository:
    def get_user(self, cursor: cursor, user_id: int) -> UserMenuEntity | None:
        cursor.execute("SELECT id, position, metadata FROM user_menu WHERE id=%s", (user_id, ))
        user = cursor.fetchone()
        if user is None:
            return None
        return UserMenuEntity(*user)
    
    def create_user(self, cursor: cursor, user: UserMenuEntity) -> bool:
        try:
            cursor.execute("INSERT INTO user_menu(id, metadata, position) VALUES (%s, %s, %s)", (user.id, Json(user.metadata), user.position))
            return True
        except Exception as e:
            print(f"Error while creating user {user.id}:\n==============\n{e}\n==============)")
            return False
    
    def change_user(self, cursor: cursor, user: UserMenuEntity) -> bool:
        try:
            cursor.execute("UPDATE user_menu SET metadata=%s, position=%s WHERE id=%s", (Json(user.metadata), user.position, user.id))
            return True
        except Exception as e:
            print(f"Error while changing user {user.id}:\n==============\n{e}\n==============)")
            return False
    