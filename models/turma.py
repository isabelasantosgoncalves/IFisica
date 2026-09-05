from datetime import date

from database.db import obter_cursor
from models.constantes import TIPO_PADRAO

COLUNAS = """
    idTurma, nome, descricao, dataCriacao, nivel,
    idUsuarioGerente, idSolicitacao, tipo
"""


def criar(id_gerente, id_solicitacao, nome, descricao, nivel,
          tipo=TIPO_PADRAO):
    sql = """
        INSERT INTO Turma
        (nome, descricao, dataCriacao, nivel,
         idUsuarioGerente, idSolicitacao, tipo)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    valores = (
        nome,
        descricao,
        date.today(),
        nivel,
        id_gerente,
        id_solicitacao,
        tipo
    )

    with obter_cursor(commit=True) as cursor:
        cursor.execute(sql, valores)
        return cursor.lastrowid


def listar_por_gerente(id_gerente):
    sql = f"""
        SELECT {COLUNAS}
        FROM Turma
        WHERE idUsuarioGerente = %s
        ORDER BY dataCriacao DESC, idTurma DESC
    """

    with obter_cursor(dicionario=True) as cursor:
        cursor.execute(sql, (id_gerente,))
        return cursor.fetchall()


def buscar(id_turma, id_gerente):
    sql = f"""
        SELECT {COLUNAS}
        FROM Turma
        WHERE idTurma = %s AND idUsuarioGerente = %s
    """

    with obter_cursor(dicionario=True) as cursor:
        cursor.execute(sql, (id_turma, id_gerente))
        return cursor.fetchone()


def atualizar(id_turma, id_gerente, nome, descricao, nivel):
    sql = """
        UPDATE Turma
        SET nome = %s,
            descricao = %s,
            nivel = %s
        WHERE idTurma = %s AND idUsuarioGerente = %s
    """

    with obter_cursor(commit=True) as cursor:
        cursor.execute(sql, (nome, descricao, nivel, id_turma, id_gerente))
        return cursor.rowcount


def excluir(id_turma, id_gerente):
    sql = "DELETE FROM Turma WHERE idTurma = %s AND idUsuarioGerente = %s"

    with obter_cursor(commit=True) as cursor:
        cursor.execute(sql, (id_turma, id_gerente))
        return cursor.rowcount
