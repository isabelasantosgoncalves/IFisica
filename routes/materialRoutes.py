import mysql.connector
from flask import Blueprint, jsonify, request, session

from models import material as modelo_material
from models import turma as modelo_turma
from routes.seguranca import login_obrigatorio_api
from routes.utilitarios import formatar_datas, texto_ou_nulo

material_bp = Blueprint("material", __name__)

LIMITE_URL = 500


def e_responsavel(id_turma):
    turma = modelo_turma.buscar(id_turma, session["idUsuario"])
    return turma is not None


def tem_acesso(id_turma):
    return modelo_turma.buscar_para_usuario(id_turma, session["idUsuario"]) is not None


def ler_campos(dados):
    assunto = texto_ou_nulo(dados.get("assunto"))
    titulo = texto_ou_nulo(dados.get("titulo"))
    descricao = texto_ou_nulo(dados.get("descricao"))
    tipo = (texto_ou_nulo(dados.get("tipo")) or "").lower()
    url = texto_ou_nulo(dados.get("url"))
    try:
        id_arquivo = dados.get("idArquivo")
        id_arquivo = int(id_arquivo) if id_arquivo else None
    except (TypeError, ValueError):
        id_arquivo = None

    if not assunto or not titulo:
        return None, "Informe o assunto e o título do material."

    if tipo not in modelo_material.TIPOS:
        return None, "Escolha se o material é um link ou um PDF."

    if tipo == modelo_material.TIPO_LINK:
        if not url:
            return None, "Informe o endereço do link."

        if not url.startswith(("http://", "https://")):
            return None, "O link precisa começar com http:// ou https://."

        if len(url) > LIMITE_URL:
            return None, "O link é longo demais."

        id_arquivo = None

    else:
        if not id_arquivo:
            return None, "Envie o arquivo PDF."

        url = None

    return (assunto, titulo, descricao, tipo, url, id_arquivo), None


def apresentar(material):
    if material["tipo"] == modelo_material.TIPO_PDF and material["idArquivo"]:
        material["url"] = f"/api/arquivos/{material['idArquivo']}"

    return formatar_datas(material, "dataCriacao")


@material_bp.route("/turmas/<int:id_turma>/materiais", methods=["GET"])
@login_obrigatorio_api
def listar_materiais(id_turma):

    if not tem_acesso(id_turma):
        return jsonify({"erro": "Você não tem acesso a esta sala."}), 403

    try:
        materiais = modelo_material.listar_por_turma(id_turma)

    except mysql.connector.Error as erro:
        return jsonify({
            "erro": "Erro ao buscar os materiais.",
            "detalhes": str(erro)
        }), 500

    return jsonify([apresentar(m) for m in materiais]), 200


@material_bp.route("/turmas/<int:id_turma>/materiais", methods=["POST"])
@login_obrigatorio_api
def criar_material(id_turma):

    if not e_responsavel(id_turma):
        return jsonify({
            "erro": "Só o responsável pela sala pode adicionar materiais."
        }), 403

    campos, erro = ler_campos(request.get_json(silent=True) or {})

    if erro:
        return jsonify({"erro": erro}), 400

    try:
        id_material = modelo_material.criar(id_turma, *campos)

    except mysql.connector.Error as erro_banco:
        return jsonify({
            "erro": "Erro ao salvar o material.",
            "detalhes": str(erro_banco)
        }), 500

    return jsonify({
        "mensagem": "Material adicionado!",
        "idMaterial": id_material
    }), 201


@material_bp.route("/turmas/<int:id_turma>/materiais/<int:id_material>", methods=["PUT"])
@login_obrigatorio_api
def atualizar_material(id_turma, id_material):

    if not e_responsavel(id_turma):
        return jsonify({
            "erro": "Só o responsável pela sala pode editar materiais."
        }), 403

    campos, erro = ler_campos(request.get_json(silent=True) or {})

    if erro:
        return jsonify({"erro": erro}), 400

    try:
        alterados = modelo_material.atualizar(id_material, id_turma, *campos)

    except mysql.connector.Error as erro_banco:
        return jsonify({
            "erro": "Erro ao atualizar o material.",
            "detalhes": str(erro_banco)
        }), 500

    if not alterados:
        return jsonify({"erro": "Material não encontrado."}), 404

    return jsonify({"mensagem": "Material atualizado!"}), 200


@material_bp.route("/turmas/<int:id_turma>/materiais/<int:id_material>", methods=["DELETE"])
@login_obrigatorio_api
def excluir_material(id_turma, id_material):

    if not e_responsavel(id_turma):
        return jsonify({
            "erro": "Só o responsável pela sala pode excluir materiais."
        }), 403

    try:
        removidos = modelo_material.excluir(id_material, id_turma)

    except mysql.connector.Error as erro_banco:
        return jsonify({
            "erro": "Erro ao excluir o material.",
            "detalhes": str(erro_banco)
        }), 500

    if not removidos:
        return jsonify({"erro": "Material não encontrado."}), 404

    return jsonify({"mensagem": "Material excluído."}), 200
