from datetime import date

import mysql.connector
from flask import Blueprint, jsonify, request, session

from database.db import conectar_banco
from routes.seguranca import login_obrigatorio_api

turma_bp = Blueprint("turma", __name__)


@turma_bp.route("/turmas", methods=["POST"])
@login_obrigatorio_api
def criar_turma():

    dados = request.get_json()

    nomeTurma = dados.get("nomeTurma")
    descricao = dados.get("descricao")
    idDocente = session["idDocente"]
    nivelEscolaridade = dados.get("nivelEscolaridade")

    if not nomeTurma:
        return jsonify({
            "erro": "O nome da turma é obrigatório."
        }), 400

    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()

        sql = """
            INSERT INTO Turma
            (nomeTurma, descricao, dataCriacao, idDocente, nivelEscolaridade)
            VALUES (%s, %s, %s, %s, %s)
        """

        valores = (
            nomeTurma,
            descricao,
            date.today(),
            idDocente,
            nivelEscolaridade
        )

        cursor.execute(sql, valores)
        conexao.commit()

        id_turma = cursor.lastrowid

        cursor.close()
        conexao.close()

        return jsonify({
            "mensagem": "Turma criada com sucesso!",
            "idTurma": id_turma
        }), 201

    except mysql.connector.Error as erro:

        return jsonify({
            "erro": "Erro ao cadastrar turma.",
            "detalhes": str(erro)
        }), 500


@turma_bp.route("/turmas", methods=["GET"])
@login_obrigatorio_api
def listar_turmas():

    try:
        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM Turma WHERE idDocente = %s ORDER BY dataCriacao DESC",
            (session["idDocente"],)
        )

        turmas = cursor.fetchall()

        cursor.close()
        conexao.close()

        return jsonify(turmas), 200

    except mysql.connector.Error as erro:

        return jsonify({
            "erro": "Erro ao buscar turmas.",
            "detalhes": str(erro)
        }), 500


@turma_bp.route("/turmas/<int:id_turma>", methods=["GET"])
@login_obrigatorio_api
def buscar_turma(id_turma):

    try:
        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)

        sql = "SELECT * FROM Turma WHERE idTurma = %s AND idDocente = %s"

        cursor.execute(sql, (id_turma, session["idDocente"]))

        turma = cursor.fetchone()

        cursor.close()
        conexao.close()

        if not turma:
            return jsonify({
                "erro": "Turma não encontrada."
            }), 404

        return jsonify(turma), 200

    except mysql.connector.Error as erro:

        return jsonify({
            "erro": "Erro ao buscar turma.",
            "detalhes": str(erro)
        }), 500


@turma_bp.route("/turmas/<int:id_turma>", methods=["PUT"])
@login_obrigatorio_api
def atualizar_turma(id_turma):

    dados = request.get_json()

    nome_turma = dados.get("nomeTurma")
    descricao = dados.get("descricao")
    nivel_escolaridade = dados.get("nivelEscolaridade")

    if not nome_turma:
        return jsonify({
            "erro": "O nome da turma é obrigatório."
        }), 400

    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()

        sql = """
            UPDATE Turma
            SET nomeTurma = %s,
                descricao = %s,
                nivelEscolaridade = %s
            WHERE idTurma = %s AND idDocente = %s
        """

        valores = (
            nome_turma,
            descricao,
            nivel_escolaridade,
            id_turma,
            session["idDocente"]
        )

        cursor.execute(sql, valores)
        conexao.commit()

        if cursor.rowcount == 0:
            cursor.close()
            conexao.close()

            return jsonify({
                "erro": "Turma não encontrada."
            }), 404

        cursor.close()
        conexao.close()

        return jsonify({
            "mensagem": "Turma atualizada com sucesso!"
        }), 200

    except mysql.connector.Error as erro:

        return jsonify({
            "erro": "Erro ao atualizar turma.",
            "detalhes": str(erro)
        }), 500


@turma_bp.route("/turmas/<int:id_turma>", methods=["DELETE"])
@login_obrigatorio_api
def excluir_turma(id_turma):

    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()

        sql = "DELETE FROM Turma WHERE idTurma = %s AND idDocente = %s"

        cursor.execute(sql, (id_turma, session["idDocente"]))
        conexao.commit()

        if cursor.rowcount == 0:
            cursor.close()
            conexao.close()

            return jsonify({
                "erro": "Turma não encontrada."
            }), 404

        cursor.close()
        conexao.close()

        return jsonify({
            "mensagem": "Turma excluída com sucesso!"
        }), 200

    except mysql.connector.Error as erro:

        return jsonify({
            "erro": "Erro ao excluir turma.",
            "detalhes": str(erro)
        }), 500


@turma_bp.route("/api/origem", methods=["POST"])
@login_obrigatorio_api
def registrar_origem():

    dados = request.get_json()

    origem = dados.get("origem")

    if not origem:
        return jsonify({
            "erro": "Selecione uma opção."
        }), 400

    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()

        cursor.execute(
            "UPDATE Docente SET origemDivulgacao = %s WHERE idDocente = %s",
            (origem, session["idDocente"])
        )
        conexao.commit()

        cursor.close()
        conexao.close()

        return jsonify({
            "mensagem": "Resposta registrada!"
        }), 200

    except mysql.connector.Error as erro:

        return jsonify({
            "erro": "Erro ao registrar resposta.",
            "detalhes": str(erro)
        }), 500
