import sys
import time

from db.crud import get_existing_items, insert_items, delete_items
from db.DB import Database
from config import Config
import argparse
import logging
import aiohttp
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler


def is_valid_record(record: dict[str: int]) -> bool:
    lac = record.get("lac")
    cellid = record.get("cellid")
    eci = record.get("eci")

    # Допускаются оба варианта: только lac или lac+cellid.
    if (lac is not None) and (0 < lac < 0xFFFF) and (cellid is None or (0 < cellid < 0xFFFF)) and (eci is None):
        return True

    # Если задан eci, то lac и cellid должны быть None.
    elif (eci is not None) and (0 < eci < 0xFFFFFFF) and (lac is None) and (cellid is None):
        return True

    return False


async def fetch_api(config: Config) -> list[dict]:
    url = config.API_URL
    logging.info(f"API request sent: {url}")
    try:
        async with aiohttp.ClientSession() as session:
            auth = aiohttp.BasicAuth(login=config.API_USER, password=config.API_PASSWORD.get_secret_value())
            async with session.get(url, auth=auth) as response:
                if response.status != 200:
                    logging.error(f"API request error: {response.status}|{await response.json()}")
                    return []
                data = await response.json()
                logging.info(f"API request completed, received {len(data)} records")
                return data
    except Exception as e:
        logging.error(f"API request error: {str(e)}")
        return []


async def synchronize(config: Config, db: Database):
    start_time = time.time()
    data = await fetch_api(config)
    if not data:
        return

    # Валидация записей
    api_set = {(record["lac"], record["cellid"], record["eci"]) for record in data if is_valid_record(record)}
    logging.info(f"After validation {len(data) - len(api_set)} records were ignored, {len(api_set)} records remained")

    db_set = await get_existing_items(await db.get_pool())
    db_set_without_id = {(d[1], d[2], d[3]) for d in db_set}

    to_insert = api_set - db_set_without_id
    to_delete = {row for row in db_set if (row[1], row[2], row[3]) not in api_set}

    await delete_items(await db.get_pool(), to_delete)
    await insert_items(await db.get_pool(), to_insert)

    logging.info(f"Job synchronize competed in {time.time() - start_time:.3f} seconds,"
                 f" DELETED {len(to_delete)} records, INSERTED {len(to_insert)} records")


async def get_db(config: Config) -> Database:
    db = Database(
        config.DB_HOST,
        config.DB_USER,
        config.DB_PASSWORD.get_secret_value(),
        config.DB_NAME,
        config.DB_PORT)
    await db.create_pool()
    return db


def get_config(env_path: str) -> Config:
    return Config(_env_file=env_path)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "config_path",
        help="Путь к файлу конфигурации (например, .env)"
    )
    return parser.parse_args()


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s.%(msecs)03d %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def configure_scheduler(config, db):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(synchronize, "interval", seconds=config.SCHEDULER_INTERVAL,
                      args=[config, db])
    scheduler.start()


async def main():
    configure_logging()
    logging.info("Configuring app")

    args = get_args()
    config = get_config(args.config_path)
    db = await get_db(config)

    logging.info("App configured")

    configure_scheduler(config, db)

    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
