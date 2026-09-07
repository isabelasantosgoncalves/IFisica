import mysql.connector
from flask import Blueprint, jsonify, request, session

from models import atividade as modelo_atividade
from models import turma as modelo_turma
from models import resposta_atividade as modelo_resposta

from routes.seguranca import login_obrigatorio_api

resposta_bp = Blueprint("resposta", __name__)


@resposta_bp.route(
    "/turmas/<int:id_turma>/atividades/<int:id_atividade>/questoes",
    methods=["GET"]
)
@login_obrigatorio_api
def obter_questoes_para_responder(id_turma, id_atividade):
    if not modelo_turma.buscar_para_usuario(id_turma, session["idUsuario"]):
        return jsonify({"erro": "Você não tem acesso a esta turma."}), 403

    atividade = modelo_atividade.buscar(id_atividade, id_turma)
    if not atividade:
        return jsonify({"erro": "Atividade não encontrada."}), 404

    ja_feita = modelo_resposta.ja_respondeu(id_atividade, session["idUsuario"])
    if ja_feita:
        detalhes = modelo_resposta.buscar_detalhe(id_atividade, session["idUsuario"])
        return jsonify({
            "atividade": atividade,
            "jaRespondida": True,
            "pontuacao": ja_feita["pontuacao"],
            "total": ja_feita["totalQuestoes"],
            "erros": ja_feita["totalQuestoes"] - ja_feita["pontuacao"],
            "detalhes": detalhes
        }), 200

    questoes = modelo_atividade.listar_exercicios_para_responder(id_atividade)

    return jsonify({
        "atividade": atividade,
        "jaRespondida": False,
        "questoes": questoes
    }), 200


@resposta_bp.route(
    "/turmas/<int:id_turma>/atividades/<int:id_atividade>/respostas",
    methods=["POST"]
)
@login_obrigatorio_api
def responder_atividade(id_turma, id_atividade):
    if not modelo_turma.buscar_para_usuario(id_turma, session["idUsuario"]):
        return jsonify({"erro": "Você não tem acesso a esta turma."}), 403

    if not modelo_atividade.buscar(id_atividade, id_turma):
        return jsonify({"erro": "Atividade não encontrada."}), 404

    if modelo_resposta.ja_respondeu(id_atividade, session["idUsuario"]):
        return jsonify({"erro": "Você já respondeu esta atividade."}), 409

    dados = request.get_json(silent=True) or {}
    respostas_brutas = dados.get("respostas", {})

    if not isinstance(respostas_brutas, dict) or not respostas_brutas:
        return jsonify({"erro": "Envie as respostas."}), 400

    try:
        respostas = {int(k): str(v).strip().upper() for k, v in respostas_brutas.items()}
    except (TypeError, ValueError):
        return jsonify({"erro": "Formato de respostas inválido."}), 400

    if any(v not in {"A", "B", "C", "D"} for v in respostas.values()):
        return jsonify({"erro": "Resposta inválida em uma das questões."}), 400

    try:
        resultado = modelo_resposta.registrar(id_atividade, session["idUsuario"], respostas)
    except mysql.connector.Error as erro:
        return jsonify({"erro": "Erro ao registrar respostas.", "detalhes": str(erro)}), 500

    return jsonify({
        "mensagem": "Respostas registradas!",
        "acertos": resultado["acertos"],
        "erros": resultado["erros"],
        "total": resultado["total"],
        "detalhes": resultado["detalhes"]
    }), 201