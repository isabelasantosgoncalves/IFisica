from flask import Blueprint, redirect, render_template, session, url_for

from models import solicitacao as modelo_solicitacao
from models.constantes import GENEROS, NIVEIS, PAPEL_ADMINISTRADOR
from routes.seguranca import (
    ensino_obrigatorio,
    login_obrigatorio,
    papel_atual,
    papel_obrigatorio,
    pode_ensinar,
    usuario_logado
)
pagina_bp = Blueprint("pagina", __name__)
@pagina_bp.route("/turma/<int:id_turma>/atividades/<int:id_atividade>")
@login_obrigatorio
def responderAtividade(id_turma, id_atividade):
    return render_template(
        "responderAtividade.html",
        id_turma=id_turma,
        id_atividade=id_atividade
    )




@pagina_bp.route("/")
def index():
    if usuario_logado():
        return redirect(url_for("pagina.telaInicial"))
    return render_template("index.html")


@pagina_bp.route("/cadastro")
def cadastro():
    return render_template("cadastro.html", generos=GENEROS)


@pagina_bp.route("/login")
def login():
    return render_template("login.html")


@pagina_bp.route("/inicio")
@login_obrigatorio
def telaInicial():
    papel = papel_atual()
    administra = papel == PAPEL_ADMINISTRADOR

    return render_template(
        "telaInicial.html",
        nome=session.get("nomeUsuario"),
        papel=papel,
        ensina=pode_ensinar(),
        administra=administra,
        pendentesAdmin=modelo_solicitacao.contar_pendentes() if administra else 0
    )


@pagina_bp.route("/nova-turma")
@ensino_obrigatorio
def novaTurma():
    return render_template("turma.html")


@pagina_bp.route("/nova-turma/escolaridade")
@ensino_obrigatorio
def escolaridade():
    return render_template("escolaridade.html", niveis=NIVEIS)


@pagina_bp.route("/turma/<int:id_turma>")
@login_obrigatorio
def pagTurma(id_turma):
    return render_template("pagTurma.html", id_turma=id_turma)


@pagina_bp.route("/solicitar-tutor")
@login_obrigatorio
def solicitarTutor():
    return render_template("solicitarTutor.html")


@pagina_bp.route("/admin/solicitacoes")
@papel_obrigatorio(PAPEL_ADMINISTRADOR)
def painelAdmin():
    return render_template("painelAdmin.html")


@pagina_bp.route("/ajuda")
def ajuda():
    return render_template("ajuda.html")


@pagina_bp.route("/logout")
def sair():
    session.clear()
    return redirect(url_for("pagina.index"))
