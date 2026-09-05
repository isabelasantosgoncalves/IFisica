import mysql.connector
from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from models import usuario as modelo_usuario
from models.constantes import CODIGOS_GENERO, GENERO_AUTODECLARACAO
from routes.seguranca import abrir_sessao
from routes.utilitarios import texto_ou_nulo

auth_bp = Blueprint("auth", __name__)

OBRIGATORIOS = ("nome", "email", "telefone", "senha", "dataNasc")


@auth_bp.route("/usuarios", methods=["POST"])
def cadastrar_usuario():

    dados = request.get_json(silent=True) or {}

    campos = {
        chave: texto_ou_nulo(dados.get(chave))
        for chave in OBRIGATORIOS
    }

    faltando = [chave for chave, valor in campos.items() if not valor]

    if faltando:
        return jsonify({
            "erro": "Preencha todos os campos.",
            "campos": faltando
        }), 400

    if len(campos["senha"]) < 6:
        return jsonify({
            "erro": "A senha deve ter pelo menos 6 caracteres."
        }), 400

    genero = texto_ou_nulo(dados.get("genero"))
    genero_autodeclarado = texto_ou_nulo(dados.get("generoAutodeclarado"))

    if genero and genero not in CODIGOS_GENERO:
        return jsonify({"erro": "Opção de gênero inválida."}), 400

    if genero == GENERO_AUTODECLARACAO and not genero_autodeclarado:
        return jsonify({
            "erro": "Escreva como você se autodeclara."
        }), 400

    if genero != GENERO_AUTODECLARACAO:
        genero_autodeclarado = None

    try:
        id_usuario = modelo_usuario.criar(
            campos["nome"],
            campos["email"],
            campos["telefone"],
            generate_password_hash(campos["senha"]),
            campos["dataNasc"],
            genero,
            genero_autodeclarado
        )

    except mysql.connector.IntegrityError:

        return jsonify({
            "erro": "Já existe um cadastro com esse e-mail ou telefone."
        }), 409

    except mysql.connector.Error as erro:

        return jsonify({
            "erro": "Erro ao cadastrar usuário.",
            "detalhes": str(erro)
        }), 500

    abrir_sessao(id_usuario, campos["nome"])

    return jsonify({
        "mensagem": "Cadastro realizado com sucesso!",
        "idUsuario": id_usuario
    }), 201


@auth_bp.route("/login", methods=["POST"])
def entrar():

    dados = request.get_json(silent=True) or {}

    email = texto_ou_nulo(dados.get("email"))
    senha = dados.get("senha")

    if not email or not senha:
        return jsonify({
            "erro": "Informe e-mail e senha."
        }), 400

    try:
        usuario = modelo_usuario.buscar_por_email(email)

    except mysql.connector.Error as erro:

        return jsonify({
            "erro": "Erro ao realizar login.",
            "detalhes": str(erro)
        }), 500

    if not usuario or not check_password_hash(usuario["senha"], senha):
        return jsonify({
            "erro": "E-mail ou senha incorretos."
        }), 401

    abrir_sessao(usuario["idUsuario"], usuario["nome"])

    return jsonify({
        "mensagem": "Login realizado com sucesso!",
        "nome": usuario["nome"]
    }), 200
