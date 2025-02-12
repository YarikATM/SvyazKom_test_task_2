import asyncpg
from typing import List, Dict, Tuple
from asyncpg.pool import Pool


class Database:
    def __init__(self, host, user, password, name, port):

        self.db_url = f"postgres://{user}:{password}@{host}:{port}/{name}"
        self._pool = None

    async def get_pool(self) -> Pool:
        return self._pool

    async def create_pool(self):
        self._pool = await asyncpg.create_pool(self.db_url)
