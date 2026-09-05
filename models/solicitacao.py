from datetime import date

from database.db import obter_cursor
from models.constantes import (
    SOLICITACAO_APROVADA,
    SOLICITACAO_PENDENTE,
    SOLICITACAO_RECUSADA
)

COLUNAS = """
    s.idSolicitacao, s.dataSolicitacao, s.motivo, s.conteudo,
    s.publicoAlvo, s.status, s.dataDecisao, s.idUsuario, s.idAdmin
"""

DADOS_SOLICITANTE = "u.nome, u.email"


def criar(id_usuario, motivo, conteudo, publico_alvo):
    sql = """
        INSERT INTO Solicitacao
        (dataSolicitacao, motivo, conteudo, publicoAlvo, status, idUsuario)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    valores = (
        date.today(),
        motivo,
        conteudo,
        publico_alvo,
        SOLICITACAO_PENDENTE,
        id_usuario
    )

    with obter_cursor(commit=True) as cursor:
        cursor.execute(sql, valores)
        return cursor.lastrowid


def buscar_por_usuario(id_usuario):
    sql = f"""
        SELECT {COLUNAS}
        FROM Solicitacao s
        WHERE s.idUsuario = %s
        ORDER BY s.idSolicitacao DESC
        LIMIT 1
    """

    with obter_cursor(dicionario=True) as cursor:
        cursor.execute(sql, (id_usuario,))
        return cursor.fetchone()


def id_aprovada_do_usuario(id_usuario):
    sql = """
        SELECT idSolicitacao
        FROM Solicitacao
        WHERE idUsuario = %s AND status = %s
        ORDER BY idSolicitacao DESC
        LIMIT 1
    """

    with obter_cursor(dicionario=True) as cursor:
        cursor.execute(sql, (id_usuario, SOLICITACAO_APROVADA))
        linha = cursor.fetchone()
        return linha["idSolicitacao"] if linha else None


def listar_pendentes():
    sql = f"""
        SELECT {COLUNAS}, {DADOS_SOLICITANTE}
        FROM Solicitacao s
        JOIN Usuario u ON u.idUsuario = s.idUsuario
        WHERE s.status = %s
        ORDER BY s.dataSolicitacao, s.idSolicitacao
    """

    with obter_cursor(dicionario=True) as cursor:
        cursor.execute(sql, (SOLICITACAO_PENDENTE,))
        return cursor.fetchall()


def buscar(id_solicitacao):
    sql = f"""
        SELECT {COLUNAS}, {DADOS_SOLICITANTE}
        FROM Solicitacao s
        JOIN Usuario u ON u.idUsuario = s.idUsuario
        WHERE s.idSolicitacao = %s
    """

    with obter_cursor(dicionario=True) as cursor:
        cursor.execute(sql, (id_solicitacao,))
        return cursor.fetchone()


def decidir(id_solicitacao, id_admin, aprovar):
    sql = """
        UPDATE Solicitacao
        SET status = %s, dataDecisao = %s, idAdmin = %s
        WHERE idSolicitacao = %s AND status = %s
    """

    novo_status = SOLICITACAO_APROVADA if aprovar else SOLICITACAO_RECUSADA

    valores = (
        novo_status,
        date.today(),
        id_admin,
        id_solicitacao,
        SOLICITACAO_PENDENTE
    )

    with obter_cursor(commit=True) as cursor:
        cursor.execute(sql, valores)
        return cursor.rowcount
