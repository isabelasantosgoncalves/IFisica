from datetime import date

import mysql.connector

from flask import (
    Blueprint,
    jsonify,
    request,
    session
)

from database.db import obter_cursor

from models import turma as modelo_turma

from models.constantes import (
    SOLICITACAO_PENDENTE,
    SOLICITACAO_APROVADA
)

from routes.seguranca import (
    login_obrigatorio_api,
    pode_ensinar
)
from routes.utilitarios import formatar_datas


sala_bp = Blueprint(
    "sala",
    __name__
)


@sala_bp.route(
    "/salas/entrar",
    methods=["POST"]
)
@login_obrigatorio_api
def solicitar_entrada():

    dados = (
        request.get_json(
            silent=True
        ) or {}
    )

    codigo = (
        dados.get("codigo")
        or ""
    ).strip().upper()


    if not codigo:

        return jsonify({
            "erro":
                "Informe o código da sala."
        }), 400


    turma = modelo_turma.buscar_por_codigo(
        codigo
    )


    if not turma:

        return jsonify({
            "erro":
                "Código de sala inválido."
        }), 404


    id_usuario = session["idUsuario"]


    if turma["idUsuarioGerente"] == id_usuario:

        return jsonify({
            "erro":
                "Você é o responsável por esta sala."
        }), 400


    try:

        with obter_cursor(
            dicionario=True,
            commit=True
        ) as cursor:

            # Já participa?
            cursor.execute(
                """
                SELECT 1
                FROM Participacao
                WHERE idUsuario = %s
                AND idTurma = %s
                """,
                (
                    id_usuario,
                    turma["idTurma"]
                )
            )

            if cursor.fetchone():

                return jsonify({
                    "erro":
                        "Você já participa desta sala."
                }), 409


            # Já possui solicitação pendente?
            cursor.execute(
                """
                SELECT idSolicitacaoEntrada
                FROM SolicitacaoEntrada

                WHERE idUsuario = %s
                AND idTurma = %s
                AND status = %s

                LIMIT 1
                """,
                (
                    id_usuario,
                    turma["idTurma"],
                    SOLICITACAO_PENDENTE
                )
            )

            if cursor.fetchone():

                return jsonify({
                    "erro":
                        "Sua solicitação já está aguardando aprovação."
                }), 409


            # Cria a solicitação
            cursor.execute(
                """
                INSERT INTO SolicitacaoEntrada
                (
                    dataSolicitacao,
                    status,
                    idUsuario,
                    idTurma
                )

                VALUES (%s, %s, %s, %s)
                """,
                (
                    date.today(),
                    SOLICITACAO_PENDENTE,
                    id_usuario,
                    turma["idTurma"]
                )
            )


            return jsonify({
                "mensagem":
                    "Solicitação de entrada enviada!",
                "idTurma":
                    turma["idTurma"]
            }), 201


    except mysql.connector.Error as erro:

        return jsonify({
            "erro":
                "Erro ao solicitar entrada.",
            "detalhes":
                str(erro)
        }), 500

@sala_bp.route(
    "/turmas/<int:id_turma>/solicitacoes-entrada",
    methods=["GET"]
)
@login_obrigatorio_api
def listar_solicitacoes_entrada(id_turma):

    id_usuario = session["idUsuario"]


    try:

        with obter_cursor(
            dicionario=True
        ) as cursor:

            cursor.execute(
                """
                SELECT 1
                FROM Turma
                WHERE idTurma = %s
                AND idUsuarioGerente = %s
                """,
                (
                    id_turma,
                    id_usuario
                )
            )

            if not cursor.fetchone():

                return jsonify({
                    "erro":
                        "Sala não encontrada."
                }), 404


            cursor.execute(
                """
                SELECT
                    s.idSolicitacaoEntrada,
                    s.dataSolicitacao,
                    s.status,
                    u.idUsuario,
                    u.nome,
                    u.email

                FROM SolicitacaoEntrada s

                INNER JOIN Usuario u
                    ON u.idUsuario = s.idUsuario

                WHERE s.idTurma = %s
                AND s.status = %s

                ORDER BY
                    s.dataSolicitacao DESC
                """,
                (id_turma, SOLICITACAO_PENDENTE)
            )

            solicitacoes = cursor.fetchall()


        return jsonify([
            formatar_datas(s, "dataSolicitacao")
            for s in solicitacoes
        ]), 200


    except mysql.connector.Error as erro:

        return jsonify({
            "erro":
                "Erro ao buscar solicitações.",
            "detalhes":
                str(erro)
        }), 500


@sala_bp.route(
    "/solicitacoes-entrada/<int:id_solicitacao>",
    methods=["PUT"]
)
@login_obrigatorio_api
def decidir_entrada(id_solicitacao):

    dados = (
        request.get_json(
            silent=True
        ) or {}
    )

    aprovar = dados.get("aprovar")


    if not isinstance(
        aprovar,
        bool
    ):

        return jsonify({
            "erro":
                "Informe se a solicitação será aprovada ou recusada."
        }), 400


    id_usuario = session["idUsuario"]


    try:

        with obter_cursor(
            dicionario=True,
            commit=True
        ) as cursor:

            cursor.execute(
                """
                SELECT
                    s.idSolicitacaoEntrada,
                    s.idUsuario,
                    s.idTurma,
                    s.status

                FROM SolicitacaoEntrada s

                INNER JOIN Turma t
                    ON t.idTurma = s.idTurma

                WHERE
                    s.idSolicitacaoEntrada = %s

                AND
                    t.idUsuarioGerente = %s
                """,
                (
                    id_solicitacao,
                    id_usuario
                )
            )

            solicitacao = cursor.fetchone()


            if not solicitacao:

                return jsonify({
                    "erro":
                        "Solicitação não encontrada."
                }), 404


            if solicitacao["status"] != SOLICITACAO_PENDENTE:

                return jsonify({
                    "erro":
                        "Esta solicitação já foi analisada."
                }), 409


            novo_status = (
                SOLICITACAO_APROVADA
                if aprovar
                else 2
            )


            cursor.execute(
                """
                UPDATE SolicitacaoEntrada

                SET status = %s

                WHERE idSolicitacaoEntrada = %s
                """,
                (
                    novo_status,
                    id_solicitacao
                )
            )


            if aprovar:

                cursor.execute(
                    """
                    INSERT INTO Participacao
                    (
                        idUsuario,
                        idTurma
                    )

                    VALUES (%s, %s)
                    """,
                    (
                        solicitacao["idUsuario"],
                        solicitacao["idTurma"]
                    )
                )


        return jsonify({
            "mensagem":
                "Entrada aprovada."
                if aprovar
                else
                "Entrada recusada."
        }), 200


    except mysql.connector.Error as erro:

        return jsonify({
            "erro":
                "Erro ao decidir solicitação.",
            "detalhes":
                str(erro)
        }), 500