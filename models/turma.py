from datetime import date
import random
import string

from database.db import obter_cursor
from models.constantes import ROTULOS_NIVEL


COLUNAS_PREFIXADAS = """
    Turma.idTurma,
    Turma.nome,
    Turma.descricao,
    Turma.dataCriacao,
    Turma.nivel,
    Turma.idUsuarioGerente,
    Turma.idSolicitacao,
    Turma.tipo,
    Turma.codigoConvite
"""

COLUNAS = """
    idTurma,
    nome,
    descricao,
    dataCriacao,
    nivel,
    idUsuarioGerente,
    idSolicitacao,
    tipo,
    codigoConvite
"""


def gerar_codigo():
    caracteres = string.ascii_uppercase + string.digits

    return "".join(
        random.choices(caracteres, k=8)
    )


def gerar_codigo_unico():
    with obter_cursor(dicionario=True) as cursor:

        for _ in range(20):

            codigo = gerar_codigo()

            cursor.execute(
                """
                SELECT idTurma
                FROM Turma
                WHERE codigoConvite = %s
                """,
                (codigo,)
            )

            if not cursor.fetchone():
                return codigo

    raise RuntimeError(
        "Não foi possível gerar um código de convite."
    )


def rotulo_do_nivel(nivel):
    return ROTULOS_NIVEL.get(nivel, "Sem nível")


def criar(
    id_gerente,
    id_solicitacao,
    nome,
    descricao,
    nivel
):

    codigo = gerar_codigo_unico()

    tipo = rotulo_do_nivel(nivel)

    sql = """
        INSERT INTO Turma
        (
            nome,
            descricao,
            dataCriacao,
            nivel,
            idUsuarioGerente,
            idSolicitacao,
            tipo,
            codigoConvite
        )
        VALUES
        (
            %s, %s, %s, %s,
            %s, %s, %s, %s
        )
    """

    valores = (
        nome,
        descricao,
        date.today(),
        nivel,
        id_gerente,
        id_solicitacao,
        tipo,
        codigo
    )

    with obter_cursor(commit=True) as cursor:

        cursor.execute(sql, valores)

        return cursor.lastrowid


def listar_por_gerente(id_gerente):

    sql = f"""
        SELECT {COLUNAS},
            (
                SELECT COUNT(*)
                FROM SolicitacaoEntrada se
                WHERE se.idTurma = Turma.idTurma
                AND se.status = 0
            ) AS pedidosPendentes
        FROM Turma
        WHERE idUsuarioGerente = %s
        ORDER BY dataCriacao DESC
    """

    with obter_cursor(dicionario=True) as cursor:

        cursor.execute(
            sql,
            (id_gerente,)
        )

        return cursor.fetchall()


def buscar(id_turma, id_gerente):

    sql = f"""
        SELECT {COLUNAS}
        FROM Turma
        WHERE idTurma = %s
        AND idUsuarioGerente = %s
    """

    with obter_cursor(dicionario=True) as cursor:

        cursor.execute(
            sql,
            (
                id_turma,
                id_gerente
            )
        )

        return cursor.fetchone()


def buscar_para_usuario(id_turma, id_usuario):

    sql = f"""
        SELECT {COLUNAS_PREFIXADAS}, u.nome AS nomeGerente
        FROM Turma
        INNER JOIN Usuario u
            ON u.idUsuario = Turma.idUsuarioGerente
        WHERE Turma.idTurma = %s
        AND (
            Turma.idUsuarioGerente = %s
            OR EXISTS (
                SELECT 1
                FROM Participacao p
                WHERE p.idTurma = Turma.idTurma
                AND p.idUsuario = %s
            )
        )
    """

    with obter_cursor(dicionario=True) as cursor:

        cursor.execute(
            sql,
            (
                id_turma,
                id_usuario,
                id_usuario
            )
        )

        return cursor.fetchone()


def buscar_por_codigo(codigo):

    sql = f"""
        SELECT {COLUNAS}
        FROM Turma
        WHERE codigoConvite = %s
    """

    with obter_cursor(dicionario=True) as cursor:

        cursor.execute(
            sql,
            (codigo,)
        )

        return cursor.fetchone()


def atualizar(
    id_turma,
    id_gerente,
    nome,
    descricao,
    nivel
):

    sql = """
        UPDATE Turma

        SET nome = %s,
            descricao = %s,
            nivel = %s,
            tipo = %s

        WHERE idTurma = %s
        AND idUsuarioGerente = %s
    """

    with obter_cursor(commit=True) as cursor:

        cursor.execute(
            sql,
            (
                nome,
                descricao,
                nivel,
                rotulo_do_nivel(nivel),
                id_turma,
                id_gerente
            )
        )

        return cursor.rowcount


def excluir(id_turma, id_gerente):

    sql = """
        DELETE FROM Turma

        WHERE idTurma = %s
        AND idUsuarioGerente = %s
    """

    with obter_cursor(commit=True) as cursor:

        cursor.execute(
            sql,
            (
                id_turma,
                id_gerente
            )
        )

        return cursor.rowcount


def listar_participantes(id_turma):

    sql = """
        SELECT
            u.idUsuario,
            u.nome,
            u.email,
            p.idTurma

        FROM Participacao p

        INNER JOIN Usuario u
            ON u.idUsuario = p.idUsuario

        WHERE p.idTurma = %s

        ORDER BY u.nome
    """

    with obter_cursor(dicionario=True) as cursor:

        cursor.execute(
            sql,
            (id_turma,)
        )

        return cursor.fetchall()

def listar_por_participante(id_usuario):

    sql = f"""
        SELECT {COLUNAS_PREFIXADAS}, u.nome AS nomeGerente
        FROM Turma
        INNER JOIN Participacao p
            ON p.idTurma = Turma.idTurma
        INNER JOIN Usuario u
            ON u.idUsuario = Turma.idUsuarioGerente
        WHERE p.idUsuario = %s
        ORDER BY Turma.dataCriacao DESC
    """

    with obter_cursor(dicionario=True) as cursor:
        cursor.execute(sql, (id_usuario,))
        return cursor.fetchall()
