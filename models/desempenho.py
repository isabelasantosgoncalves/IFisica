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
