import mysql.connector
from flask import Blueprint, jsonify, request

from models import exercicio as modelo_exercicio
from routes.seguranca import login_obrigatorio_api, tutor_obrigatorio_api
from routes.utilitarios import texto_ou_nulo

exercicio_bp = Blueprint("exercicio", __name__)

ALTERNATIVAS_VALIDAS = {"A", "B", "C", "D"}


def validar_payload(dados):
    pergunta = texto_ou_nulo(dados.get("pergunta"))
    materia = texto_ou_nulo(dados.get("materia"))
    dificuldade = texto_ou_nulo(dados.get("dificuldade"))
    alternativa_certa = texto_ou_nulo(dados.get("alternativaCerta"))
    resolucao = texto_ou_nulo(dados.get("resolucao"))
    imagem = texto_ou_nulo(dados.get("imagem"))

    alternativas = {
        letra: texto_ou_nulo(dados.get(f"alternativa{letra}"))
        for letra in ALTERNATIVAS_VALIDAS
    }

    erros = []
    if not pergunta:
        erros.append("O enunciado é obrigatório.")
    if not materia:
        erros.append("A matéria é obrigatória.")
    if not dificuldade:
        erros.append("A dificuldade é obrigatória.")
    if alternativa_certa not in ALTERNATIVAS_VALIDAS:
        erros.append("Escolha a alternativa correta (A, B, C ou D).")
    if any(not v for v in alternativas.values()):
        erros.append("Preencha as quatro alternativas.")

    return (pergunta, alternativas, alternativa_certa, materia, dificuldade,
            resolucao, imagem), erros


@exercicio_bp.route("/exercicios", methods=["POST"])
@tutor_obrigatorio_api
def criar_exercicio():
    dados = request.get_json(silent=True) or {}
    campos, erros = validar_payload(dados)

    if erros:
        return jsonify({"erro": erros[0]}), 400

    try:
        id_exercicio = modelo_exercicio.criar(*campos)
    except mysql.connector.Error as erro:
        return jsonify({"erro": "Erro ao criar questão.", "detalhes": str(erro)}), 500

    return jsonify({"mensagem": "Questão criada!", "idExercicio": id_exercicio}), 201


@exercicio_bp.route("/exercicios", methods=["GET"])
@tutor_obrigatorio_api
def listar_exercicios():
    materia = request.args.get("materia")
    dificuldade = request.args.get("dificuldade")

    try:
        exercicios = modelo_exercicio.listar(materia, dificuldade)
    except mysql.connector.Error as erro:
        return jsonify({"erro": "Erro ao buscar questões.", "detalhes": str(erro)}), 500

    return jsonify(exercicios), 200


@exercicio_bp.route("/exercicios/<int:id_exercicio>", methods=["PUT"])
@tutor_obrigatorio_api
def atualizar_exercicio(id_exercicio):
    dados = request.get_json(silent=True) or {}
    campos, erros = validar_payload(dados)

    if erros:
        return jsonify({"erro": erros[0]}), 400

    if not modelo_exercicio.buscar(id_exercicio):
        return jsonify({"erro": "Questão não encontrada."}), 404

    try:
        modelo_exercicio.atualizar(id_exercicio, *campos)
    except mysql.connector.Error as erro:
        return jsonify({"erro": "Erro ao atualizar questão.", "detalhes": str(erro)}), 500

    return jsonify({"mensagem": "Questão atualizada!"}), 200


@exercicio_bp.route("/exercicios/<int:id_exercicio>", methods=["DELETE"])
@tutor_obrigatorio_api
def excluir_exercicio(id_exercicio):
    try:
        removido = modelo_exercicio.excluir(id_exercicio)
    except mysql.connector.Error as erro:
        return jsonify({
            "erro": "Não foi possível excluir: a questão já está em uso em alguma atividade.",
            "detalhes": str(erro)
        }), 409

    if not removido:
        return jsonify({"erro": "Questão não encontrada."}), 404

    return jsonify({"mensagem": "Questão excluída."}), 200