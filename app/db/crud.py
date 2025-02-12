from typing import List, Tuple, Set
from asyncpg.pool import Pool
import logging
import asyncio


async def get_existing_items(pool: Pool) -> set:
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT id, lac, cellid, eci FROM location_data")
        return {(row["id"], row["lac"], row["cellid"], row["eci"]) for row in rows}




async def delete_items(pool: Pool, to_delete: Tuple[Tuple[int, int, int, int]]):
    if not to_delete:
        return
    ids_to_delete = {row[0] for row in to_delete}
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM location_data WHERE id = ANY($1)", ids_to_delete)
    for id, lac, cellid, eci in to_delete:
        logging.info(f"INSERTED: (id={id}, lac={lac}, cellid={cellid}, eci={eci})")






async def insert_items(pool: Pool, to_insert: Tuple[Tuple[int, int, int]]):
    if not to_insert:
        return
    async with pool.acquire() as conn:
        await conn.executemany(
            "INSERT INTO location_data (lac, cellid, eci) VALUES ($1, $2, $3)",
            to_insert)

    for lac, cellid, eci in to_insert:
        logging.info(f"INSERTED: (lac={lac}, cellid={cellid}, eci={eci})")

