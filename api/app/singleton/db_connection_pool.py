from app import env_config

from psycopg_pool import AsyncConnectionPool
from psycopg.conninfo import make_conninfo


_connection_pool = None


def _get_db_conninfo():
    # TODO: load database password from a secret
    return make_conninfo(
        host=env_config.DB_HOST,
        port=env_config.DB_PORT,
        dbname=env_config.DB_NAME,
        user=env_config.DB_USER,
        password=env_config.DB_PASSWORD,
    )


async def _get_pool():
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = AsyncConnectionPool(_get_db_conninfo(), open=False)
        await _connection_pool.open()
        await _connection_pool.wait()
    return _connection_pool


async def get_connection(timeout=None):
    pool = await _get_pool()
    return pool.connection(timeout)