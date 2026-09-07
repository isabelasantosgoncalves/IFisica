import time
from contextlib import contextmanager

import mysql.connector
from mysql.connector import pooling

from config import Config

_pool = None

TENTATIVAS = 3
ESPERA_ENTRE_TENTATIVAS = 0.4


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
            collation="utf8mb4_unicode_ci",
            connection_timeout=Config.DB_TIMEOUT
        )

    return _pool


def pegar_conexao():
    """A rede ate o servidor e instavel: uma falha isolada nao deve virar erro
    na tela. Tenta de novo antes de desistir, e so a obtencao da conexao -
    nenhuma consulta e repetida, para nao gravar nada duas vezes."""
    ultimo_erro = None

    for tentativa in range(TENTATIVAS):
        try:
            return obter_pool().get_connection()
        except mysql.connector.Error as erro:
            ultimo_erro = erro

            if tentativa < TENTATIVAS - 1:
                time.sleep(ESPERA_ENTRE_TENTATIVAS)

    raise ultimo_erro


@contextmanager
def obter_cursor(dicionario=False, commit=False):
    conexao = pegar_conexao()
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
