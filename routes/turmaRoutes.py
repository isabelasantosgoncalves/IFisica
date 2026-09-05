import mysql.connector
from flask import Blueprint, jsonify, request, session

from models import solicitacao as modelo_solicitacao
from models import turma as modelo_turma
from models.constantes import CODIGOS_NIVEL, ROTULOS_NIVEL
from routes.seguranca import login_obrigatorio_api, tutor_obrigatorio_api
from routes.utilitarios import formatar_datas, texto_ou_nulo

turma_bp = Blueprint("turma", __name__)


def ler_nivel(dados):
    try:
        nivel = int(dados.get("nivel"))
    except (TypeError, ValueError):
        return None

    return nivel if nivel in CODIGOS_NIVEL else None


def apresentar(turma):
    turma["nivelRotulo"] = ROTULOS_NIVEL.get(turma["nivel"], "Sem nível")
    return formatar_datas(turma, "dataCriacao")


@turma_bp.route("/turmas", methods=["POST"])
@tutor_obrigatorio_api
def criar_turma():

    dados = request.get_json(silent=True) or {}

    nome = texto_ou_nulo(dados.get("nome"))
    descricao = texto_ou_nulo(dados.get("descricao"))
    nivel = ler_nivel(dados)

    if not nome:
        return jsonify({"erro": "O nome da turma é obrigatório."}), 400

    if nivel is None:
        return jsonify({"erro": "Selecione um nível de escolaridade."}), 400

    try:
        id_solicitacao = modelo_solicitacao.id_aprovada_do_usuario(
            session["idUsuario"]
        )

        if not id_solicitacao:
            return jsonify({
                "erro": "Sua permissão de tutor ainda não foi aprovada."
            }), 403

        id_turma = modelo_turma.criar(
            session["idUsuario"], id_solicitacao, nome, descricao, nivel
        )

    except mysql.connector.IntegrityError:

        return jsonify({
            "erro": "Já existe uma turma com esse nome."
        }), 409

    except mysql.connector.Error as erro:

        return jsonify({
            "erro": "Erro ao cadastrar turma.",
            "detalhes": str(erro)
        }), 500

    return jsonify({
        "mensagem": "Turma criada com sucesso!",
        "idTurma": id_turma
    }), 201


@turma_bp.route("/turmas", methods=["GET"])
@login_obrigatorio_api
def listar_turmas():

    try:
        turmas = modelo_turma.listar_por_gerente(session["idUsuario"])

    except mysql.connector.Error as erro:

        return jsonify({
            "erro": "Erro ao buscar turmas.",
            "detalhes": str(erro)
        }), 500

    return jsonify([apresentar(turma) for turma in turmas]), 200


@turma_bp.route("/turmas/<int:id_turma>", methods=["GET"])
@login_obrigatorio_api
def buscar_turma(id_turma):

    try:
        turma = modelo_turma.buscar(id_turma, session["idUsuario"])

    except mysql.connector.Error as erro:

        return jsonify({
            "erro": "Erro ao buscar turma.",
            "detalhes": str(erro)
        }), 500

    if not turma:
        return jsonify({"erro": "Turma não encontrada."}), 404

    return jsonify(apresentar(turma)), 200


@turma_bp.route("/turmas/<int:id_turma>", methods=["PUT"])
@login_obrigatorio_api
def atualizar_turma(id_turma):

    dados = request.get_json(silent=True) or {}

    nome = texto_ou_nulo(dados.get("nome"))
    descricao = texto_ou_nulo(dados.get("descricao"))
    nivel = ler_nivel(dados)

    if not nome:
        return jsonify({"erro": "O nome da turma é obrigatório."}), 400

    if nivel is None:
        return jsonify({"erro": "Selecione um nível de escolaridade."}), 400

    try:
        alteradas = modelo_turma.atualizar(
            id_turma, session["idUsuario"], nome, descricao, nivel
        )

    except mysql.connector.IntegrityError:

        return jsonify({
            "erro": "Já existe uma turma com esse nome."
        }), 409

    except mysql.connector.Error as erro:

        return jsonify({
            "erro": "Erro ao atualizar turma.",
            "detalhes": str(erro)
        }), 500

    if not alteradas:
        return jsonify({"erro": "Turma não encontrada."}), 404

    return jsonify({"mensagem": "Turma atualizada com sucesso!"}), 200


@turma_bp.route("/turmas/<int:id_turma>", methods=["DELETE"])
@login_obrigatorio_api
def excluir_turma(id_turma):

    try:
        removidas = modelo_turma.excluir(id_turma, session["idUsuario"])

    except mysql.connector.Error as erro:

        return jsonify({
            "erro": "Erro ao excluir turma.",
            "detalhes": str(erro)
        }), 500

    if not removidas:
        return jsonify({"erro": "Turma não encontrada."}), 404

    return jsonify({"mensagem": "Turma excluída com sucesso!"}), 200
