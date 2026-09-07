import mysql.connector

from flask import (
    Blueprint,
    jsonify,
    request,
    session
)

from models import atividade as modelo_atividade
from models import turma as modelo_turma

from routes.seguranca import (
    login_obrigatorio_api,
    tutor_obrigatorio_api
)



from routes.utilitarios import formatar_datas, texto_ou_nulo


atividade_bp = Blueprint(
    "atividade",
    __name__
)


def obter_ids_exercicios(dados):
    exercicios = dados.get("exercicios", [])

    if not isinstance(exercicios, list):
        return None

    resultado = []

    for valor in exercicios:
        try:
            id_exercicio = int(valor)
        except (TypeError, ValueError):
            return None

        if id_exercicio not in resultado:
            resultado.append(id_exercicio)

    return resultado


def usuario_tem_acesso_turma(id_turma):
    return modelo_turma.buscar_para_usuario(
        id_turma,
        session["idUsuario"]
    )


@atividade_bp.route(
    "/turmas/<int:id_turma>/atividades",
    methods=["POST"]
)
@tutor_obrigatorio_api
def criar_atividade(id_turma):

    turma = modelo_turma.buscar(
        id_turma,
        session["idUsuario"]
    )

    if not turma:
        return jsonify({
            "erro": "Turma não encontrada ou você não é o responsável por ela."
        }), 404

    dados = request.get_json(
        silent=True
    ) or {}

    nome = texto_ou_nulo(
        dados.get("nome")
    )

    descricao = texto_ou_nulo(
        dados.get("descricao")
    )

    exercicios = obter_ids_exercicios(
        dados
    )

    if not nome:
        return jsonify({
            "erro": "O nome da atividade é obrigatório."
        }), 400

    if exercicios is None:
        return jsonify({
            "erro": "Lista de questões inválida."
        }), 400

    if not exercicios:
        return jsonify({
            "erro": "Selecione pelo menos uma questão."
        }), 400

    try:
        id_atividade = modelo_atividade.criar(
            nome,
            descricao,
            id_turma,
            exercicios
        )

    except mysql.connector.Error as erro:
        return jsonify({
            "erro": "Erro ao criar atividade.",
            "detalhes": str(erro)
        }), 500

    return jsonify({
        "mensagem": "Atividade criada com sucesso!",
        "idAtividade": id_atividade
    }), 201


@atividade_bp.route(
    "/turmas/<int:id_turma>/atividades",
    methods=["GET"]
)
@login_obrigatorio_api
def listar_atividades(id_turma):

    turma = usuario_tem_acesso_turma(
        id_turma
    )

    if not turma:
        return jsonify({
            "erro": "Você não tem acesso a esta turma."
        }), 403

    try:
        atividades = modelo_atividade.listar_por_turma(
            id_turma
        )

    except mysql.connector.Error as erro:
        return jsonify({
            "erro": "Erro ao buscar atividades.",
            "detalhes": str(erro)
        }), 500

    return jsonify([
        formatar_datas(a, "dataCriacao")
        for a in atividades
    ]), 200


@atividade_bp.route(
    "/turmas/<int:id_turma>/atividades/<int:id_atividade>",
    methods=["GET"]
)
@login_obrigatorio_api
def buscar_atividade(
    id_turma,
    id_atividade
):

    turma = usuario_tem_acesso_turma(
        id_turma
    )

    if not turma:
        return jsonify({
            "erro": "Você não tem acesso a esta turma."
        }), 403

    atividade = modelo_atividade.buscar(
        id_atividade,
        id_turma
    )

    if not atividade:
        return jsonify({
            "erro": "Atividade não encontrada."
        }), 404

    atividade["exercicios"] = (
        modelo_atividade.listar_exercicios(
            id_atividade
        )
    )

    return jsonify(
        atividade
    ), 200


@atividade_bp.route(
    "/turmas/<int:id_turma>/atividades/<int:id_atividade>",
    methods=["PUT"]
)
@tutor_obrigatorio_api
def atualizar_atividade(
    id_turma,
    id_atividade
):

    turma = modelo_turma.buscar(
        id_turma,
        session["idUsuario"]
    )

    if not turma:
        return jsonify({
            "erro": "Turma não encontrada ou você não é o responsável por ela."
        }), 404

    dados = request.get_json(
        silent=True
    ) or {}

    nome = texto_ou_nulo(
        dados.get("nome")
    )

    descricao = texto_ou_nulo(
        dados.get("descricao")
    )

    exercicios = obter_ids_exercicios(
        dados
    )

    if not nome:
        return jsonify({
            "erro": "O nome da atividade é obrigatório."
        }), 400

    if exercicios is None or not exercicios:
        return jsonify({
            "erro": "Selecione pelo menos uma questão."
        }), 400

    try:
        atualizada = modelo_atividade.atualizar(
            id_atividade,
            id_turma,
            nome,
            descricao,
            exercicios
        )

    except mysql.connector.Error as erro:
        return jsonify({
            "erro": "Erro ao atualizar atividade.",
            "detalhes": str(erro)
        }), 500

    if not atualizada:
        return jsonify({
            "erro": "Atividade não encontrada."
        }), 404

    return jsonify({
        "mensagem": "Atividade atualizada com sucesso!"
    }), 200


@atividade_bp.route(
    "/turmas/<int:id_turma>/atividades/<int:id_atividade>",
    methods=["DELETE"]
)
@tutor_obrigatorio_api
def excluir_atividade(
    id_turma,
    id_atividade
):

    turma = modelo_turma.buscar(
        id_turma,
        session["idUsuario"]
    )

    if not turma:
        return jsonify({
            "erro": "Turma não encontrada ou você não é o responsável por ela."
        }), 404

    try:
        removida = modelo_atividade.excluir(
            id_atividade,
            id_turma
        )

    except mysql.connector.Error as erro:
        return jsonify({
            "erro": "Erro ao excluir atividade.",
            "detalhes": str(erro)
        }), 500

    if not removida:
        return jsonify({
            "erro": "Atividade não encontrada."
        }), 404

    return jsonify({
        "mensagem": "Atividade excluída com sucesso!"
    }), 200