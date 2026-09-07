import mysql.connector

from flask import (
    Blueprint,
    jsonify,
    request,
    session
)

from models import solicitacao as modelo_solicitacao
from models import turma as modelo_turma

from models.constantes import (
    CODIGOS_NIVEL,
    ROTULOS_NIVEL
)

from routes.seguranca import login_obrigatorio_api
from routes.utilitarios import (
    formatar_datas,
    texto_ou_nulo
)


turma_bp = Blueprint(
    "turma",
    __name__
)


def ler_nivel(dados):

    try:
        nivel = int(
            dados.get("nivel")
        )

    except (
        TypeError,
        ValueError
    ):
        return None

    if nivel in CODIGOS_NIVEL:
        return nivel

    return None


def apresentar(turma):

    turma["nivelRotulo"] = (
        ROTULOS_NIVEL.get(
            turma["nivel"],
            "Sem nível"
        )
    )

    return formatar_datas(
        turma,
        "dataCriacao"
    )


def usuario_pode_gerenciar():

    id_usuario = session["idUsuario"]

    return (
        modelo_solicitacao
        .id_aprovada_do_usuario(
            id_usuario
        )
        is not None
    )


@turma_bp.route(
    "/turmas",
    methods=["POST"]
)
@login_obrigatorio_api
def criar_turma():

    if not usuario_pode_gerenciar():

        return jsonify({
            "erro":
                "Você ainda não possui permissão "
                "para criar salas."
        }), 403


    dados = (
        request.get_json(
            silent=True
        ) or {}
    )


    nome = texto_ou_nulo(
        dados.get("nome")
    )

    descricao = texto_ou_nulo(
        dados.get("descricao")
    )

    nivel = ler_nivel(
        dados
    )


    if not nome:

        return jsonify({
            "erro":
                "O nome da sala é obrigatório."
        }), 400


    if nivel is None:

        return jsonify({
            "erro":
                "Selecione um nível de escolaridade."
        }), 400


    try:

        id_solicitacao = (
            modelo_solicitacao
            .id_aprovada_do_usuario(
                session["idUsuario"]
            )
        )


        if not id_solicitacao:

            return jsonify({
                "erro":
                    "Sua permissão ainda não foi aprovada."
            }), 403


        id_turma = modelo_turma.criar(
            session["idUsuario"],
            id_solicitacao,
            nome,
            descricao,
            nivel
        )


    except mysql.connector.IntegrityError:

        return jsonify({
            "erro":
                "Você já possui uma sala com esse nome."
        }), 409


    except mysql.connector.Error as erro:

        return jsonify({
            "erro":
                "Erro ao criar sala.",
            "detalhes":
                str(erro)
        }), 500


    return jsonify({
        "mensagem":
            "Sala criada com sucesso!",

        "idTurma":
            id_turma
    }), 201


@turma_bp.route(
    "/turmas",
    methods=["GET"]
)
@login_obrigatorio_api
def listar_turmas():

    try:

        turmas = (
            modelo_turma
            .listar_por_gerente(
                session["idUsuario"]
            )
        )

    except mysql.connector.Error as erro:

        return jsonify({
            "erro":
                "Erro ao buscar salas.",
            "detalhes":
                str(erro)
        }), 500


    return jsonify([
        apresentar(turma)
        for turma in turmas
    ]), 200


@turma_bp.route(
    "/turmas/<int:id_turma>",
    methods=["GET"]
)
@login_obrigatorio_api
def buscar_turma(id_turma):

    try:

        turma = modelo_turma.buscar_para_usuario(
            id_turma,
            session["idUsuario"]
        )

    except mysql.connector.Error as erro:

        return jsonify({
            "erro":
                "Erro ao buscar sala.",
            "detalhes":
                str(erro)
        }), 500


    if not turma:

        return jsonify({
            "erro":
                "Sala não encontrada."
        }), 404


    sou_gerente = turma["idUsuarioGerente"] == session["idUsuario"]

    turma["souGerente"] = sou_gerente

    if not sou_gerente:
        turma["codigoConvite"] = None

    return jsonify(
        apresentar(turma)
    ), 200


@turma_bp.route(
    "/turmas/minhas-participacoes",
    methods=["GET"]
)
@login_obrigatorio_api
def listar_participacoes():

    try:

        turmas = modelo_turma.listar_por_participante(
            session["idUsuario"]
        )

    except mysql.connector.Error as erro:

        return jsonify({
            "erro":
                "Erro ao buscar suas salas.",
            "detalhes":
                str(erro)
        }), 500

    for turma in turmas:
        turma["codigoConvite"] = None

    return jsonify([
        apresentar(turma) for turma in turmas
    ]), 200


@turma_bp.route(
    "/turmas/<int:id_turma>/participantes",
    methods=["GET"]
)
@login_obrigatorio_api
def listar_participantes(id_turma):

    turma = modelo_turma.buscar(
        id_turma,
        session["idUsuario"]
    )

    if not turma:

        return jsonify({
            "erro":
                "Sala não encontrada."
        }), 404

    try:

        participantes = (
            modelo_turma
            .listar_participantes(
                id_turma
            )
        )

    except mysql.connector.Error as erro:

        return jsonify({
            "erro":
                "Erro ao buscar participantes.",
            "detalhes":
                str(erro)
        }), 500

    return jsonify(
        participantes
    ), 200


@turma_bp.route(
    "/turmas/<int:id_turma>",
    methods=["PUT"]
)
@login_obrigatorio_api
def atualizar_turma(id_turma):

    if not usuario_pode_gerenciar():

        return jsonify({
            "erro":
                "Você não possui permissão para gerenciar salas."
        }), 403


    dados = (
        request.get_json(
            silent=True
        ) or {}
    )


    nome = texto_ou_nulo(
        dados.get("nome")
    )

    descricao = texto_ou_nulo(
        dados.get("descricao")
    )

    nivel = ler_nivel(
        dados
    )


    if not nome:

        return jsonify({
            "erro":
                "O nome da sala é obrigatório."
        }), 400


    if nivel is None:

        return jsonify({
            "erro":
                "Selecione um nível de escolaridade."
        }), 400


    try:

        alteradas = (
            modelo_turma.atualizar(
                id_turma,
                session["idUsuario"],
                nome,
                descricao,
                nivel
            )
        )

    except mysql.connector.IntegrityError:

        return jsonify({
            "erro":
                "Você já possui uma sala com esse nome."
        }), 409


    except mysql.connector.Error as erro:

        return jsonify({
            "erro":
                "Erro ao atualizar sala.",
            "detalhes":
                str(erro)
        }), 500


    if not alteradas:

        return jsonify({
            "erro":
                "Sala não encontrada."
        }), 404


    return jsonify({
        "mensagem":
            "Sala atualizada com sucesso!"
    }), 200


@turma_bp.route(
    "/turmas/<int:id_turma>",
    methods=["DELETE"]
)
@login_obrigatorio_api
def excluir_turma(id_turma):

    if not usuario_pode_gerenciar():

        return jsonify({
            "erro":
                "Você não possui permissão para gerenciar salas."
        }), 403


    try:

        removidas = (
            modelo_turma.excluir(
                id_turma,
                session["idUsuario"]
            )
        )

    except mysql.connector.Error as erro:

        return jsonify({
            "erro":
                "Erro ao excluir sala.",
            "detalhes":
                str(erro)
        }), 500


    if not removidas:

        return jsonify({
            "erro":
                "Sala não encontrada."
        }), 404


    return jsonify({
        "mensagem":
            "Sala excluída com sucesso!"
    }), 200