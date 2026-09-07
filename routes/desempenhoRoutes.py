import mysql.connector
from flask import Blueprint, jsonify, session

from models import desempenho as modelo_desempenho
from models import turma as modelo_turma
from routes.seguranca import login_obrigatorio_api

desempenho_bp = Blueprint("desempenho", __name__)


@desempenho_bp.route("/turmas/<int:id_turma>/ranking", methods=["GET"])
@login_obrigatorio_api
def ranking(id_turma):

    if not modelo_turma.buscar_para_usuario(id_turma, session["idUsuario"]):
        return jsonify({"erro": "Você não tem acesso a esta sala."}), 403

    try:
        linhas = modelo_desempenho.ranking_da_turma(id_turma)

    except mysql.connector.Error as erro:
        return jsonify({
            "erro": "Erro ao montar o ranking.",
            "detalhes": str(erro)
        }), 500

    for linha in linhas:
        linha["souEu"] = linha["idUsuario"] == session["idUsuario"]

    return jsonify(linhas), 200


@desempenho_bp.route("/meu-progresso", methods=["GET"])
@login_obrigatorio_api
def meu_progresso():

    try:
        progresso = modelo_desempenho.progresso_do_usuario(session["idUsuario"])

    except mysql.connector.Error as erro:
        return jsonify({
            "erro": "Erro ao buscar seu progresso.",
            "detalhes": str(erro)
        }), 500

    return jsonify(progresso), 200
