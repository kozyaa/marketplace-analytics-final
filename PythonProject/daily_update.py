import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine, text

load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import config
from data_collector_v2 import MarketplaceDataCollector

LOG_DIR = 'logs'
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

log_filename = f"{LOG_DIR}/daily_update.log"

file_handler = RotatingFileHandler(
    log_filename,
    maxBytes=10 * 1024 * 1024,
    backupCount=5,
    encoding='utf-8'
)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)
logger = logging.getLogger(__name__)


def main():
    yesterday = datetime.now() - timedelta(days=1)
    date_str = yesterday.strftime('%Y-%m-%d')

    logger.info(f"Обновление данных за {date_str}")

    collector = MarketplaceDataCollector()
    data = collector.fetch_data_for_date(date_str)

    if not data:
        logger.warning(f"Данные за {date_str} не получены")
        return

    df = collector.process_data(data, date_str)
    if df is None:
        logger.warning(f"Ошибка обработки данных за {date_str}")
        return

    collector.save_to_csv(df, date_str)

    engine = create_engine(config.DATABASE_URL)

    try:
        check_query = text("SELECT COUNT(*) FROM sales WHERE data_date = :date")
        with engine.connect() as conn:
            count = conn.execute(check_query, {"date": date_str}).scalar()

        if count > 0:
            logger.warning(f"Данные за {date_str} уже есть в БД. Пропускаем.")
            return

        df.to_sql('sales', engine, if_exists='append', index=False)
        logger.info(f"Данные за {date_str} добавлены в PostgreSQL")

    except Exception as e:
        logger.error(f"Ошибка при работе с БД: {e}")


if __name__ == "__main__":
    logger.info("Запуск daily_update.py")
    main()
    logger.info("Завершение daily_update.py")