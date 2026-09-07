import mysql.connector
from flask import Blueprint, jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from models import desempenho as modelo_desempenho
from models import perfil as modelo_perfil
from models import turma as modelo_turma
from models import usuario as modelo_usuario
from models.constantes import (
    CODIGOS_GENERO,
    GENERO_AUTODECLARACAO,
    ROTULOS_GENERO,
    ROTULOS_NIVEL
)
from routes.seguranca import login_obrigatorio_api, papel_atual
from routes.utilitarios import formatar_datas, texto_ou_nulo

perfil_bp = Blueprint("perfil", __name__)

TAMANHO_MINIMO_SENHA = 6


def ler_genero(dados):
    genero = texto_ou_nulo(dados.get("genero"))
    autodeclarado = texto_ou_nulo(dados.get("generoAutodeclarado"))

    if genero and genero not in CODIGOS_GENERO:
        return None, "Opção de gênero inválida."

    if genero == GENERO_AUTODECLARACAO and not autodeclarado:
        return None, "Escreva como você se autodeclara."

    if genero != GENERO_AUTODECLARACAO:
        autodeclarado = None

    return (genero, autodeclarado), None


@perfil_bp.route("/perfil", methods=["GET"])
@login_obrigatorio_api
def ver_perfil():

    id_usuario = session["idUsuario"]

    try:
        usuario = modelo_usuario.buscar(id_usuario)

        if not usuario:
            return jsonify({"erro": "Usuário não encontrado."}), 404

        usuario["papel"] = papel_atual()
        usuario["progresso"] = modelo_desempenho.progresso_do_usuario(id_usuario)
        usuario["salasQueGerencia"] = modelo_turma.listar_por_gerente(id_usuario)
        usuario["salasQueParticipa"] = modelo_turma.listar_por_participante(id_usuario)

    except mysql.connector.Error as erro:
        return jsonify({
            "erro": "Erro ao buscar seu perfil.",
            "detalhes": str(erro)
        }), 500

    usuario["generoRotulo"] = (
        usuario["generoAutodeclarado"]
        if usuario["genero"] == GENERO_AUTODECLARACAO
        else ROTULOS_GENERO.get(usuario["genero"])
    )

    for sala in usuario["salasQueGerencia"] + usuario["salasQueParticipa"]:
        sala["nivelRotulo"] = ROTULOS_NIVEL.get(sala["nivel"], "Sem nível")
        sala["codigoConvite"] = None
        formatar_datas(sala, "dataCriacao")

    return jsonify(formatar_datas(usuario, "dataNasc")), 200


@perfil_bp.route("/perfil", methods=["PUT"])
@login_obrigatorio_api
def atualizar_perfil():

    dados = request.get_json(silent=True) or {}

    nome = texto_ou_nulo(dados.get("nome"))
    telefone = texto_ou_nulo(dados.get("telefone"))

    if not nome or not telefone:
        return jsonify({"erro": "Nome e telefone são obrigatórios."}), 400

    genero, erro = ler_genero(dados)

    if erro:
        return jsonify({"erro": erro}), 400

    try:
        modelo_perfil.atualizar_dados(session["idUsuario"], nome, telefone, *genero)

    except mysql.connector.IntegrityError:
        return jsonify({
            "erro": "Já existe um cadastro com esse telefone."
        }), 409

    except mysql.connector.Error as erro_banco:
        return jsonify({
            "erro": "Erro ao salvar o perfil.",
            "detalhes": str(erro_banco)
        }), 500

    session["nomeUsuario"] = nome

    return jsonify({"mensagem": "Perfil atualizado!"}), 200


@perfil_bp.route("/perfil/senha", methods=["PUT"])
@login_obrigatorio_api
def trocar_senha():

    dados = request.get_json(silent=True) or {}

    atual = dados.get("senhaAtual")
    nova = dados.get("senhaNova")

    if not atual or not nova:
        return jsonify({
            "erro": "Informe a senha atual e a nova."
        }), 400

    if len(nova) < TAMANHO_MINIMO_SENHA:
        return jsonify({
            "erro": f"A nova senha deve ter pelo menos {TAMANHO_MINIMO_SENHA} caracteres."
        }), 400

    if nova == atual:
        return jsonify({
            "erro": "A nova senha precisa ser diferente da atual."
        }), 400

    try:
        guardada = modelo_perfil.buscar_senha(session["idUsuario"])

        if not guardada or not check_password_hash(guardada, atual):
            return jsonify({"erro": "A senha atual está incorreta."}), 401

        modelo_perfil.atualizar_senha(
            session["idUsuario"], generate_password_hash(nova)
        )

    except mysql.connector.Error as erro:
        return jsonify({
            "erro": "Erro ao trocar a senha.",
            "detalhes": str(erro)
        }), 500

    return jsonify({"mensagem": "Senha alterada!"}), 200
