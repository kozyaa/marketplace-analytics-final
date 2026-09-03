import requests
import pandas as pd
from datetime import datetime, timedelta
import logging
import os
import sys
import time
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import config

LOG_DIR = 'logs'
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

log_filename = f"{LOG_DIR}/data_collector.log"

# Создаём обработчик с ротацией
file_handler = RotatingFileHandler(
    log_filename,
    maxBytes=10*1024*1024,
    backupCount=5,
    encoding='utf-8'
)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# Обработчик для консоли
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Настройка корневого логгера
logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)
logger = logging.getLogger(__name__)


class MarketplaceDataCollector:
    def __init__(self):
        self.api_url = config.API_URL
        self.data_dir = "data"

        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def fetch_data_for_date(self, date_str):
        """Получение данных за конкретную дату"""
        try:
            params = {'date': date_str}
            logger.info(f"Запрашиваю данные за {date_str}")

            response = requests.get(self.api_url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            logger.info(f"Получено {len(data)} записей за {date_str}")
            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка за {date_str}: {e}")
            return None

    def process_data(self, data, date_str):
        """Обработка и преобразование данных"""
        if not data:
            logger.warning(f"Нет данных для обработки за {date_str}")
            return None

        try:
            df = pd.DataFrame(data)

            df['price_per_item_rub'] = df['price_per_item'] / 100
            df['discount_per_item_rub'] = df['discount_per_item'] / 100

            df['purchase_time'] = pd.to_datetime(
                df['purchase_time_as_seconds_from_midnight'],
                unit='s'
            ).dt.strftime('%H:%M:%S')

            df['load_date'] = datetime.now()
            df['data_date'] = date_str

            df.rename(columns={
                'client_id': 'customer_id',
                'purchase_datetime': 'order_date',
                'total_price': 'total_amount'
            }, inplace=True)

            return df

        except Exception as e:
            logger.error(f"Ошибка при обработке данных за {date_str}: {e}")
            return None

    def save_to_csv(self, df, date_str):
        """Сохранение обработанных данных в CSV"""
        if df is None or df.empty:
            logger.warning(f"Нет данных для сохранения за {date_str}")
            return

        try:
            filename = f"{self.data_dir}/sales_{date_str}.csv"
            df.to_csv(filename, index=False)
            logger.info(f"Данные сохранены в {filename}")
            return df
        except Exception as e:
            logger.error(f"Ошибка при сохранении данных за {date_str}: {e}")
            return None

    def collect_historical_data(self, start_date, end_date, delay=1):
        """Сбор исторических данных"""
        current = start_date
        successful_days = 0
        total_records = 0

        while current <= end_date:
            date_str = current.strftime('%Y-%m-%d')

            raw_data = self.fetch_data_for_date(date_str)
            if raw_data:
                processed_df = self.process_data(raw_data, date_str)
                if processed_df is not None:
                    self.save_to_csv(processed_df, date_str)
                    successful_days += 1
                    total_records += len(processed_df)

            time.sleep(delay)
            current += timedelta(days=1)

        logger.info(f"ИТОГО: собрано за {successful_days} дней, {total_records} записей")
        return successful_days, total_records


if __name__ == "__main__":
    collector = MarketplaceDataCollector()

    start = datetime(2023, 1, 1)
    end = datetime(2023, 12, 31)

    logger.info("НАЧИНАЮ СБОР ДАННЫХ...")
    collector.collect_historical_data(start, end)
    logger.info("СБОР ЗАВЕРШЕН!")
