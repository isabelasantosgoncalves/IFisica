from flask import Blueprint, redirect, render_template, session, url_for

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

    return render_template(
        "telaInicial.html",
        nome=session.get("nomeUsuario"),
        papel=papel,
        ensina=pode_ensinar(),
        administra=papel == PAPEL_ADMINISTRADOR
    )


@pagina_bp.route("/nova-turma")
@ensino_obrigatorio
def novaTurma():
    return render_template("turma.html")


@pagina_bp.route("/nova-turma/escolaridade")
@ensino_obrigatorio
def escolaridade():
    return render_template("escolaridade.html", niveis=NIVEIS)


@pagina_bp.route("/solicitar-tutor")
@login_obrigatorio
def solicitarTutor():
    return render_template("solicitarTutor.html")


@pagina_bp.route("/admin/solicitacoes")
@papel_obrigatorio(PAPEL_ADMINISTRADOR)
def painelAdmin():
    return render_template("painelAdmin.html")


@pagina_bp.route("/logout")
def sair():
    session.clear()
    return redirect(url_for("pagina.index"))
