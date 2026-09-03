from datetime import date

import mysql.connector
from flask import Blueprint, jsonify, redirect, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from database.db import conectar_banco

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/docentes", methods=["POST"])
def cadastrar_docente():

    dados = request.get_json()

    nome = dados.get("nome")
    email = dados.get("email")
    senha = dados.get("senha")
    contato = dados.get("contato")
    cpf = dados.get("cpf")
    data_nascimento = dados.get("dataNascimento")
    naturalidade = dados.get("naturalidade")

    if not nome or not email or not senha:
        return jsonify({
            "erro": "Nome, e-mail e senha são obrigatórios."
        }), 400

    if len(senha) < 6:
        return jsonify({
            "erro": "A senha deve ter pelo menos 6 caracteres."
        }), 400

    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()

        sql = """
            INSERT INTO Docente
            (nome, email, senhaHash, contato, cpf,
             dataNascimento, naturalidade, dataCadastro)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        valores = (
            nome,
            email,
            generate_password_hash(senha),
            contato,
            cpf,
            data_nascimento or None,
            naturalidade,
            date.today()
        )

        cursor.execute(sql, valores)
        conexao.commit()

        id_docente = cursor.lastrowid

        cursor.close()
        conexao.close()

        session["idDocente"] = id_docente
        session["nomeDocente"] = nome

        return jsonify({
            "mensagem": "Cadastro realizado com sucesso!",
            "idDocente": id_docente
        }), 201

    except mysql.connector.IntegrityError:

        return jsonify({
            "erro": "Já existe um cadastro com esse e-mail ou CPF."
        }), 409

    except mysql.connector.Error as erro:

        return jsonify({
            "erro": "Erro ao cadastrar docente.",
            "detalhes": str(erro)
        }), 500


@auth_bp.route("/api/login", methods=["POST"])
def entrar():

    dados = request.get_json()

    email = dados.get("email")
    senha = dados.get("senha")

    if not email or not senha:
        return jsonify({
            "erro": "Informe e-mail e senha."
        }), 400

    try:
        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute(
            "SELECT idDocente, nome, senhaHash FROM Docente WHERE email = %s",
            (email,)
        )

        docente = cursor.fetchone()

        cursor.close()
        conexao.close()

        if not docente or not check_password_hash(docente["senhaHash"], senha):
            return jsonify({
                "erro": "E-mail ou senha incorretos."
            }), 401

        session["idDocente"] = docente["idDocente"]
        session["nomeDocente"] = docente["nome"]

        return jsonify({
            "mensagem": "Login realizado com sucesso!",
            "nome": docente["nome"]
        }), 200

    except mysql.connector.Error as erro:

        return jsonify({
            "erro": "Erro ao realizar login.",
            "detalhes": str(erro)
        }), 500


@auth_bp.route("/logout")
def sair():
    session.clear()
    return redirect(url_for("pagina.index"))
