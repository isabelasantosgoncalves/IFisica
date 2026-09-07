from datetime import date

from database.db import obter_cursor


def criar(
    nome,
    descricao,
    id_turma,
    exercicios
):
    sql = """
        INSERT INTO Atividade
        (
            nome,
            descricao,
            dataCriacao,
            idTurma
        )
        VALUES (%s, %s, %s, %s)
    """

    with obter_cursor(commit=True) as cursor:

        cursor.execute(
            sql,
            (
                nome,
                descricao,
                date.today(),
                id_turma
            )
        )

        id_atividade = cursor.lastrowid

        for id_exercicio in exercicios:

            cursor.execute(
                """
                INSERT INTO AtividadeExercicio
                (
                    idAtividade,
                    idExercicio
                )
                VALUES (%s, %s)
                """,
                (
                    id_atividade,
                    id_exercicio
                )
            )

        return id_atividade


def listar_por_turma(id_turma):
    sql = """
        SELECT
            a.idAtividade,
            a.nome,
            a.descricao,
            a.dataCriacao,
            COUNT(ae.idExercicio) AS quantidadeQuestoes
        FROM Atividade a
        LEFT JOIN AtividadeExercicio ae
            ON ae.idAtividade = a.idAtividade
        WHERE a.idTurma = %s
        GROUP BY
            a.idAtividade,
            a.nome,
            a.descricao,
            a.dataCriacao
        ORDER BY
            a.dataCriacao DESC,
            a.idAtividade DESC
    """

    with obter_cursor(dicionario=True) as cursor:
        cursor.execute(sql, (id_turma,))

        return cursor.fetchall()


def buscar(id_atividade, id_turma):
    sql = """
        SELECT
            idAtividade,
            nome,
            descricao,
            dataCriacao,
            idTurma
        FROM Atividade
        WHERE idAtividade = %s
        AND idTurma = %s
    """

    with obter_cursor(dicionario=True) as cursor:
        cursor.execute(
            sql,
            (id_atividade, id_turma)
        )

        return cursor.fetchone()


def listar_exercicios(id_atividade):
    sql = """
        SELECT
            e.*
        FROM AtividadeExercicio ae
        INNER JOIN Exercicio e
            ON e.idExercicio = ae.idExercicio
        WHERE ae.idAtividade = %s
        ORDER BY e.idExercicio
    """

    with obter_cursor(dicionario=True) as cursor:
        cursor.execute(sql, (id_atividade,))

        return cursor.fetchall()


def atualizar(
    id_atividade,
    id_turma,
    nome,
    descricao,
    exercicios
):
    with obter_cursor(commit=True) as cursor:

        cursor.execute(
            """
            UPDATE Atividade
            SET nome = %s,
                descricao = %s
            WHERE idAtividade = %s
            AND idTurma = %s
            """,
            (
                nome,
                descricao,
                id_atividade,
                id_turma
            )
        )

        if cursor.rowcount == 0:
            return False

        cursor.execute(
            """
            DELETE FROM AtividadeExercicio
            WHERE idAtividade = %s
            """,
            (id_atividade,)
        )

        for id_exercicio in exercicios:

            cursor.execute(
                """
                INSERT INTO AtividadeExercicio
                (
                    idAtividade,
                    idExercicio
                )
                VALUES (%s, %s)
                """,
                (
                    id_atividade,
                    id_exercicio
                )
            )

        return True


def excluir(id_atividade, id_turma):
    sql = """
        DELETE FROM Atividade
        WHERE idAtividade = %s
        AND idTurma = %s
    """

    with obter_cursor(commit=True) as cursor:
        cursor.execute(
            sql,
            (
                id_atividade,
                id_turma
            )
        )

        return cursor.rowcount

def listar_exercicios_para_responder(id_atividade):
    sql = """
        SELECT
            e.idExercicio, e.pergunta,
            e.alternativaA, e.alternativaB, e.alternativaC, e.alternativaD,
            e.materia, e.dificuldade, e.idImagem
        FROM AtividadeExercicio ae
        INNER JOIN Exercicio e ON e.idExercicio = ae.idExercicio
        WHERE ae.idAtividade = %s
        ORDER BY ae.ordem, e.idExercicio
    """
    with obter_cursor(dicionario=True) as cursor:
        cursor.execute(sql, (id_atividade,))
        return cursor.fetchall()