from database.entities.UniversityEntity import UniversityEntity
from psycopg2._psycopg import cursor
from psycopg2.extras import Json

class UniversityRepository:
    def get_university(self, cursor: cursor, user_id: int) -> UniversityEntity | None:
        cursor.execute("SELECT id, name FROM university WHERE id=%s", (user_id, ))
        uni = cursor.fetchone()
        if uni is None:
            return None
        return UniversityEntity(*uni)
    
    def create_university(self, cursor: cursor, university: UniversityEntity) -> bool:
        try:
            cursor.execute("INSERT INTO university(name) VALUES (%s)", (university.name,))
            return True
        except Exception as e:
            print(f"Error while creating user {university.id}:\n==============\n{e}\n==============)")
            return False

    def search(self, cursor: cursor, query: str) ->  list[UniversityEntity]:
        cursor.execute("SELECT id, name from university u ORDER BY similarity(u.name, %s) DESC LIMIT 10", (query.lower(), ))
        return list(map(lambda x: UniversityEntity(*x), cursor.fetchall()))
