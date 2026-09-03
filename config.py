# config.py
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Настройки базы данных
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_NAME = os.getenv('DB_NAME', 'marketplace_db')

    # Настройки API
    API_URL = os.getenv('API_URL', 'http://final-project.simulative.ru/data')

    @property
    def DATABASE_URL(self):
        return f'postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:5432/{self.DB_NAME}'


# Создаём один экземпляр конфига для всего проекта
config = Config()
