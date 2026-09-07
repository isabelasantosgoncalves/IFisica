from database.db import obter_cursor
from models.constantes import NIVEIS_ALUNO


def ranking_da_turma(id_turma):
    sql = """
        SELECT
            u.idUsuario,
            u.nome,
            COUNT(DISTINCT ra.idAtividade) AS atividadesFeitas,
            COALESCE(SUM(ra.pontuacao), 0) AS acertos,
            COALESCE(SUM(ra.totalQuestoes), 0) AS questoes
        FROM RealizacaoAtividade ra
        INNER JOIN Atividade a
            ON a.idAtividade = ra.idAtividade
        INNER JOIN Usuario u
            ON u.idUsuario = ra.idUsuario
        WHERE a.idTurma = %s
        GROUP BY u.idUsuario, u.nome
        ORDER BY acertos DESC, questoes ASC, u.nome
    """

    with obter_cursor(dicionario=True) as cursor:
        cursor.execute(sql, (id_turma,))
        linhas = cursor.fetchall()

    posicao = 0
    acertos_anteriores = None

    for indice, linha in enumerate(linhas, start=1):
        linha["acertos"] = int(linha["acertos"])
        linha["questoes"] = int(linha["questoes"])

        if linha["acertos"] != acertos_anteriores:
            posicao = indice
            acertos_anteriores = linha["acertos"]

        linha["posicao"] = posicao
        linha["aproveitamento"] = (
            round(linha["acertos"] * 100 / linha["questoes"])
            if linha["questoes"] else 0
        )

    return linhas


def nivel_por_respondidas(respondidas):
    atual = NIVEIS_ALUNO[0]
    proximo = None

    for faixa in NIVEIS_ALUNO:
        if respondidas >= faixa[0]:
            atual = faixa
        else:
            proximo = faixa
            break

    return {
        "nivel": atual[1],
        "minimoDoNivel": atual[0],
        "proximoNivel": proximo[1] if proximo else None,
        "faltamParaOProximo": proximo[0] - respondidas if proximo else 0
    }


def progresso_do_usuario(id_usuario):
    sql = """
        SELECT
            COUNT(*) AS respondidas,
            COALESCE(SUM(r.correta), 0) AS acertos
        FROM RespostaAtividade r
        INNER JOIN RealizacaoAtividade ra
            ON ra.idRealizacao = r.idRealizacao
        WHERE ra.idUsuario = %s
    """

    with obter_cursor(dicionario=True) as cursor:
        cursor.execute(sql, (id_usuario,))
        linha = cursor.fetchone()

    respondidas = int(linha["respondidas"])
    acertos = int(linha["acertos"])

    progresso = {
        "respondidas": respondidas,
        "acertos": acertos,
        "erros": respondidas - acertos,
        "aproveitamento": round(acertos * 100 / respondidas) if respondidas else 0
    }

    progresso.update(nivel_por_respondidas(respondidas))

    return progresso


def desempenho_por_questao(id_turma):
    sql = """
        SELECT
            e.idExercicio,
            e.pergunta,
            e.materia,
            e.dificuldade,
            COUNT(r.idRespostaAtividade) AS respostas,
            COALESCE(SUM(r.correta), 0) AS acertos
        FROM Atividade a
        INNER JOIN AtividadeExercicio ae
            ON ae.idAtividade = a.idAtividade
        INNER JOIN Exercicio e
            ON e.idExercicio = ae.idExercicio
        LEFT JOIN RealizacaoAtividade ra
            ON ra.idAtividade = a.idAtividade
        LEFT JOIN RespostaAtividade r
            ON r.idRealizacao = ra.idRealizacao
            AND r.idExercicio = e.idExercicio
        WHERE a.idTurma = %s
        GROUP BY e.idExercicio, e.pergunta, e.materia, e.dificuldade
        ORDER BY e.idExercicio
    """

    with obter_cursor(dicionario=True) as cursor:
        cursor.execute(sql, (id_turma,))
        linhas = cursor.fetchall()

    for linha in linhas:
        linha["respostas"] = int(linha["respostas"])
        linha["acertos"] = int(linha["acertos"])
        linha["erros"] = linha["respostas"] - linha["acertos"]
        linha["percentualAcerto"] = (
            round(linha["acertos"] * 100 / linha["respostas"])
            if linha["respostas"] else None
        )

    return linhas


def desempenho_por_atividade(id_turma):
    sql = """
        SELECT
            a.idAtividade,
            a.nome,
            COUNT(DISTINCT ra.idUsuario) AS quemFez,
            COALESCE(SUM(ra.pontuacao), 0) AS acertos,
            COALESCE(SUM(ra.totalQuestoes), 0) AS questoes
        FROM Atividade a
        LEFT JOIN RealizacaoAtividade ra
            ON ra.idAtividade = a.idAtividade
        WHERE a.idTurma = %s
        GROUP BY a.idAtividade, a.nome
        ORDER BY a.idAtividade
    """

    with obter_cursor(dicionario=True) as cursor:
        cursor.execute(sql, (id_turma,))
        linhas = cursor.fetchall()

    for linha in linhas:
        linha["quemFez"] = int(linha["quemFez"])
        linha["acertos"] = int(linha["acertos"])
        linha["questoes"] = int(linha["questoes"])
        linha["mediaPercentual"] = (
            round(linha["acertos"] * 100 / linha["questoes"])
            if linha["questoes"] else None
        )

    return linhas


def contar_participantes(id_turma):
    sql = "SELECT COUNT(*) AS total FROM Participacao WHERE idTurma = %s"

    with obter_cursor(dicionario=True) as cursor:
        cursor.execute(sql, (id_turma,))
        return int(cursor.fetchone()["total"])


def relatorio_da_turma(id_turma):
    por_aluno = ranking_da_turma(id_turma)
    por_questao = desempenho_por_questao(id_turma)
    por_atividade = desempenho_por_atividade(id_turma)

    participantes = contar_participantes(id_turma)
    responderam = len(por_aluno)

    respondidas = sum(q["respostas"] for q in por_questao)
    acertos = sum(q["acertos"] for q in por_questao)

    dificeis = [q for q in por_questao if q["percentualAcerto"] is not None]
    dificeis.sort(key=lambda q: (q["percentualAcerto"], -q["respostas"]))

    return {
        "resumo": {
            "participantes": participantes,
            "responderam": responderam,
            "semResponder": max(participantes - responderam, 0),
            "atividades": len(por_atividade),
            "questoes": len(por_questao),
            "respostasDadas": respondidas,
            "acertos": acertos,
            "aproveitamento": round(acertos * 100 / respondidas) if respondidas else None
        },
        "porAluno": por_aluno,
        "porAtividade": por_atividade,
        "porQuestao": por_questao,
        "questoesMaisDificeis": dificeis[:5]
    }
