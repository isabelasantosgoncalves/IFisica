from database.db import obter_cursor

COLUNAS_QUESTAO = """
    e.idExercicio, e.pergunta,
    e.alternativaA, e.alternativaB, e.alternativaC, e.alternativaD,
    e.alternativaCerta, e.materia, e.dificuldade, e.resolucao, e.imagem
"""


def ja_respondeu(id_atividade, id_usuario):
    with obter_cursor(dicionario=True) as cursor:
        cursor.execute(
            "SELECT * FROM RealizacaoAtividade WHERE idAtividade = %s AND idUsuario = %s",
            (id_atividade, id_usuario)
        )
        return cursor.fetchone()


def buscar_detalhe(id_atividade, id_usuario):
    sql = f"""
        SELECT {COLUNAS_QUESTAO}, r.respostaDada, r.correta
        FROM RespostaAtividade r
        INNER JOIN RealizacaoAtividade ra
            ON ra.idRealizacao = r.idRealizacao
        INNER JOIN Exercicio e
            ON e.idExercicio = r.idExercicio
        WHERE ra.idAtividade = %s AND ra.idUsuario = %s
        ORDER BY r.idRespostaAtividade
    """

    with obter_cursor(dicionario=True) as cursor:
        cursor.execute(sql, (id_atividade, id_usuario))
        linhas = cursor.fetchall()

    for linha in linhas:
        linha["correta"] = bool(linha["correta"])

    return linhas


def registrar(id_atividade, id_usuario, respostas):
    """respostas: dict {idExercicio (int): letra ('A'..'D')}"""
    marcadores = ",".join(["%s"] * len(respostas))

    with obter_cursor(dicionario=True, commit=True) as cursor:

        cursor.execute(
            f"""
            SELECT {COLUNAS_QUESTAO}
            FROM Exercicio e
            WHERE e.idExercicio IN ({marcadores})
            """,
            tuple(respostas.keys())
        )
        questoes = {linha["idExercicio"]: linha for linha in cursor.fetchall()}

        cursor.execute(
            """
            INSERT INTO RealizacaoAtividade (idAtividade, idUsuario, totalQuestoes)
            VALUES (%s, %s, %s)
            """,
            (id_atividade, id_usuario, len(respostas))
        )
        id_realizacao = cursor.lastrowid

        acertos = 0
        detalhes = []

        for id_exercicio, resposta_dada in respostas.items():
            questao = questoes.get(id_exercicio)

            if not questao:
                continue

            correta = questao["alternativaCerta"] == resposta_dada
            acertos += int(correta)

            cursor.execute(
                """
                INSERT INTO RespostaAtividade
                (idRealizacao, idExercicio, respostaDada, correta)
                VALUES (%s, %s, %s, %s)
                """,
                (id_realizacao, id_exercicio, resposta_dada, int(correta))
            )

            detalhes.append({
                **questao,
                "respostaDada": resposta_dada,
                "correta": correta
            })

        cursor.execute(
            "UPDATE RealizacaoAtividade SET pontuacao = %s WHERE idRealizacao = %s",
            (acertos, id_realizacao)
        )

        total = len(respostas)

        return {
            "acertos": acertos,
            "erros": total - acertos,
            "total": total,
            "detalhes": detalhes
        }
