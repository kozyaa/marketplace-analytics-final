# scheduler_docker.py
import schedule
import time
from datetime import datetime
import sys
import os
import logging
from logging.handlers import RotatingFileHandler

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

LOG_DIR = 'logs'
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

log_filename = f"{LOG_DIR}/scheduler.log"

file_handler = RotatingFileHandler(
    log_filename,
    maxBytes=10*1024*1024,
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


def run_job():
    logger.info(f"Запуск обновления данных в {datetime.now()}")
    try:
        from daily_update import main
        main()
    except Exception as e:
        logger.error(f"Ошибка при обновлении: {e}")


schedule.every().day.at("07:00").do(run_job)

logger.info("Планировщик запущен. Ожидание 07:00...")

while True:
    schedule.run_pending()
    time.sleep(60)