from contextlib import contextmanager

from mysql.connector import pooling

from config import Config

_pool = None


def obter_pool():
    global _pool

    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_name="ifisica",
            pool_size=Config.DB_POOL_SIZE,
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            charset="utf8mb4",
            collation="utf8mb4_unicode_ci"
        )

    return _pool


@contextmanager
def obter_cursor(dicionario=False, commit=False):
    conexao = obter_pool().get_connection()
    cursor = conexao.cursor(dictionary=dicionario)

    try:
        yield cursor

        if commit:
            conexao.commit()

    except Exception:
        if commit:
            conexao.rollback()
        raise

    finally:
        cursor.close()
        conexao.close()
