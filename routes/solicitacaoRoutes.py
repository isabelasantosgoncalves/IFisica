import mysql.connector
from flask import Blueprint, jsonify, request, session

from models import solicitacao as modelo_solicitacao
from models.constantes import (
    ROTULOS_STATUS,
    SOLICITACAO_APROVADA,
    SOLICITACAO_PENDENTE
)
from routes.seguranca import admin_obrigatorio_api, login_obrigatorio_api
from routes.utilitarios import formatar_datas, texto_ou_nulo

solicitacao_bp = Blueprint("solicitacao", __name__)

LIMITE_TEXTO = 255


def apresentar(pedido):
    pedido["statusRotulo"] = ROTULOS_STATUS.get(pedido["status"], "Desconhecido")
    return formatar_datas(pedido, "dataSolicitacao", "dataDecisao")


@solicitacao_bp.route("/solicitacoes", methods=["POST"])
@login_obrigatorio_api
def solicitar_tutoria():

    dados = request.get_json(silent=True) or {}

    motivo = texto_ou_nulo(dados.get("motivo"))
    conteudo = texto_ou_nulo(dados.get("conteudo"))
    publico_alvo = texto_ou_nulo(dados.get("publicoAlvo"))

    if not motivo or not conteudo or not publico_alvo:
        return jsonify({
            "erro": "Preencha motivo, conteúdo e público-alvo."
        }), 400

    for texto in (motivo, conteudo, publico_alvo):
        if len(texto) > LIMITE_TEXTO:
            return jsonify({
                "erro": f"Cada campo aceita no máximo {LIMITE_TEXTO} caracteres."
            }), 400

    try:
        pedido = modelo_solicitacao.buscar_por_usuario(session["idUsuario"])

        if pedido and pedido["status"] == SOLICITACAO_PENDENTE:
            return jsonify({
                "erro": "Você já tem uma solicitação aguardando análise."
            }), 409

        if pedido and pedido["status"] == SOLICITACAO_APROVADA:
            return jsonify({
                "erro": "Você já é tutor."
            }), 409

        id_solicitacao = modelo_solicitacao.criar(
            session["idUsuario"], motivo, conteudo, publico_alvo
        )

    except mysql.connector.Error as erro:

        return jsonify({
            "erro": "Erro ao enviar solicitação.",
            "detalhes": str(erro)
        }), 500

    return jsonify({
        "mensagem": "Solicitação enviada. Aguarde a análise de um administrador.",
        "idSolicitacao": id_solicitacao
    }), 201


@solicitacao_bp.route("/solicitacoes/minha", methods=["GET"])
@login_obrigatorio_api
def minha_solicitacao():

    try:
        pedido = modelo_solicitacao.buscar_por_usuario(session["idUsuario"])

    except mysql.connector.Error as erro:

        return jsonify({
            "erro": "Erro ao buscar sua solicitação.",
            "detalhes": str(erro)
        }), 500

    if not pedido:
        return jsonify(None), 200

    return jsonify(apresentar(pedido)), 200


@solicitacao_bp.route("/solicitacoes", methods=["GET"])
@admin_obrigatorio_api
def listar_pendentes():

    try:
        pedidos = modelo_solicitacao.listar_pendentes()

    except mysql.connector.Error as erro:

        return jsonify({
            "erro": "Erro ao buscar solicitações.",
            "detalhes": str(erro)
        }), 500

    return jsonify([apresentar(pedido) for pedido in pedidos]), 200


@solicitacao_bp.route("/solicitacoes/<int:id_solicitacao>", methods=["GET"])
@admin_obrigatorio_api
def detalhar(id_solicitacao):

    try:
        pedido = modelo_solicitacao.buscar(id_solicitacao)

    except mysql.connector.Error as erro:

        return jsonify({
            "erro": "Erro ao buscar solicitação.",
            "detalhes": str(erro)
        }), 500

    if not pedido:
        return jsonify({"erro": "Solicitação não encontrada."}), 404

    return jsonify(apresentar(pedido)), 200


@solicitacao_bp.route("/solicitacoes/<int:id_solicitacao>", methods=["PUT"])
@admin_obrigatorio_api
def decidir(id_solicitacao):

    dados = request.get_json(silent=True) or {}
    aprovar = dados.get("aprovar")

    if not isinstance(aprovar, bool):
        return jsonify({
            "erro": "Informe se a solicitação foi aprovada ou recusada."
        }), 400

    try:
        analisadas = modelo_solicitacao.decidir(
            id_solicitacao, session["idUsuario"], aprovar
        )

    except mysql.connector.Error as erro:

        return jsonify({
            "erro": "Erro ao registrar a decisão.",
            "detalhes": str(erro)
        }), 500

    if not analisadas:
        return jsonify({
            "erro": "Esta solicitação já foi analisada."
        }), 409

    return jsonify({
        "mensagem": "Solicitação aprovada." if aprovar else "Solicitação recusada."
    }), 200
