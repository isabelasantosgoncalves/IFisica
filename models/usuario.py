from database.db import obter_cursor
from models.constantes import (
    PAPEL_ADMINISTRADOR,
    PAPEL_ESTUDANTE,
    PAPEL_TUTOR,
    SOLICITACAO_APROVADA
)

COLUNAS = "idUsuario, nome, email, telefone, dataNasc, genero, generoAutodeclarado"


def criar(nome, email, telefone, senha_hash, data_nasc,
          genero=None, genero_autodeclarado=None):
    sql = """
        INSERT INTO Usuario
        (nome, email, telefone, senha, dataNasc, genero, generoAutodeclarado)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    valores = (
        nome,
        email,
        telefone,
        senha_hash,
        data_nasc,
        genero,
        genero_autodeclarado
    )

    with obter_cursor(commit=True) as cursor:
        cursor.execute(sql, valores)
        return cursor.lastrowid


def buscar_por_email(email):
    sql = "SELECT idUsuario, nome, senha FROM Usuario WHERE email = %s"

    with obter_cursor(dicionario=True) as cursor:
        cursor.execute(sql, (email,))
        return cursor.fetchone()


def buscar(id_usuario):
    sql = f"SELECT {COLUNAS} FROM Usuario WHERE idUsuario = %s"

    with obter_cursor(dicionario=True) as cursor:
        cursor.execute(sql, (id_usuario,))
        return cursor.fetchone()


def e_tutor(id_usuario):
    sql = """
        SELECT idSolicitacao FROM Solicitacao
        WHERE idUsuario = %s AND status = %s
        LIMIT 1
    """

    with obter_cursor() as cursor:
        cursor.execute(sql, (id_usuario, SOLICITACAO_APROVADA))
        return cursor.fetchone() is not None


def papel(id_usuario):
    sql = """
        SELECT
            EXISTS(
                SELECT 1 FROM Admin WHERE idUsuario = %s
            ) AS administrador,
            EXISTS(
                SELECT 1 FROM Solicitacao
                WHERE idUsuario = %s AND status = %s
            ) AS tutor
    """

    with obter_cursor(dicionario=True) as cursor:
        cursor.execute(sql, (id_usuario, id_usuario, SOLICITACAO_APROVADA))
        linha = cursor.fetchone()

    if linha["administrador"]:
        return PAPEL_ADMINISTRADOR

    if linha["tutor"]:
        return PAPEL_TUTOR

    return PAPEL_ESTUDANTE
