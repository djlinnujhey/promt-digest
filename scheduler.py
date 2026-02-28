"""scheduler.py"""
import signal
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from main import run_daily

# --- Логирование ---
logging.basicConfig(
    filename="logs/scheduler.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

scheduler = BlockingScheduler(timezone="UTC")

@scheduler.scheduled_job(
    "cron",
    hour=5,
    minute=0,
    timezone="UTC",  # 08:00 UTC+3 (Московское время)
)
def scheduled_run():
    logging.info("🔔 Старт ежедневного дайджеста Prompt Engineering")
    try:
        import asyncio
        asyncio.run(run_daily())
        logging.info("✅ Дайджест успешно отправлен")
    except Exception as e:
        logging.exception(f"❌ Ошибка при отправке дайджеста: {e}")

def shutdown(signum, frame):
    logging.info("🛑 Получен сигнал завершения")
    scheduler.shutdown(wait=False)
    logging.info("Шедулер остановлен")

if __name__ == "__main__":
    # Graceful shutdown
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    logging.info("🚀 Запуск планировщика")
    scheduler.start()