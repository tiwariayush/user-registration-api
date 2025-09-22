import psycopg
from contextlib import contextmanager
from typing import Optional, Generator
from psycopg_pool import ConnectionPool

from config import get_db_dsn


_pool: Optional[ConnectionPool] = None

def init_pool(min_size: int = 1, max_size: int = 10) -> ConnectionPool:
    """
    Initialize PostgreSQL connection pool with lazy loading.
    """
    global _pool
    if _pool is None:
        dsn = get_db_dsn()
        _pool = ConnectionPool(conninfo=dsn, min_size=min_size, max_size=max_size, open=True)
    return _pool

@contextmanager 
def get_conn() -> Generator[psycopg.Connection, None, None]:
    if _pool is None:
        init_pool()
    with _pool.connection() as conn:
        yield conn
