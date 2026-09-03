# test_api.py
import requests
from datetime import datetime

# Проверяем, работает ли API
url = "http://final-project.simulative.ru/data"
params = {"date": "2023-01-01"}

try:
    response = requests.get(url, params=params)
    print(f"Статус ответа: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Получено записей: {len(data)}")
        if data:
            print(f"Первая запись: {data[0]}")
    else:
        print(f"Ошибка: {response.text}")

except Exception as e:
    print(f"Произошла ошибка: {e}")
