from contextlib import contextmanager
import psycopg2
from database.entities.UserMenuEntity import UserMenuEntity
from database.repositories.UserRepository import UserRepository
import os
from dotenv import load_dotenv

load_dotenv()
user = os.getenv("DB_USER")
password = os.getenv("DB_PASS")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")


class UserService:
    def __init__(self) -> None:
        self.__connection = psycopg2.connect(
            dbname=db_name,
            user=user,
            password=password,
            host=host,
            port=port,
        )
        self.__user_repo = UserRepository()
        self.__initializate_database()

    @contextmanager
    def __transaction(self):
        """Контекстный менеджер для безопасных транзакций"""
        try:
            yield
            self.__connection.commit()
        except Exception as e:
            self.__connection.rollback()
            raise e
    
    def get_user(self, user_id: int) -> UserMenuEntity | None:
        with self.__transaction():
            with self.__connection.cursor() as cursor:
                return self.__user_repo.get_user(cursor, user_id)
            
    def create_user(self, user: UserMenuEntity) -> bool:
        with self.__transaction():
            with self.__connection.cursor() as cursor:
                return self.__user_repo.create_user(cursor, user)
            
    def change_user(self, user: UserMenuEntity) -> bool:
        with self.__transaction():
            with self.__connection.cursor() as cursor:
                return self.__user_repo.change_user(cursor, user)
            
    def __initializate_database(self):
        with self.__transaction():
            with self.__connection.cursor() as cursor:
                cursor.execute("""
                   CREATE TABLE IF NOT EXISTS  user_menu (
                    id INT PRIMARY KEY,
                    position VARCHAR(255),
                    metadata JSONB NOT NULL
                    );
                """)
