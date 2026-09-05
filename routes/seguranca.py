from functools import wraps

from flask import jsonify, redirect, session, url_for

from models import usuario as modelo_usuario
from models.constantes import PAPEL_ADMINISTRADOR


def usuario_logado():
    return session.get("idUsuario")


def abrir_sessao(id_usuario, nome):
    session["idUsuario"] = id_usuario
    session["nomeUsuario"] = nome
    session.permanent = True


def papel_atual():
    id_usuario = usuario_logado()

    if not id_usuario:
        return None

    return modelo_usuario.papel(id_usuario)


def pode_ensinar():
    id_usuario = usuario_logado()

    if not id_usuario:
        return False

    return modelo_usuario.e_tutor(id_usuario)


def login_obrigatorio(rota):
    @wraps(rota)
    def verificar(*args, **kwargs):
        if not usuario_logado():
            return redirect(url_for("pagina.login"))
        return rota(*args, **kwargs)

    return verificar


def login_obrigatorio_api(rota):
    @wraps(rota)
    def verificar(*args, **kwargs):
        if not usuario_logado():
            return jsonify({"erro": "Sessão expirada. Faça login novamente."}), 401
        return rota(*args, **kwargs)

    return verificar


def papel_obrigatorio_api(*papeis_aceitos):
    def decorador(rota):
        @wraps(rota)
        @login_obrigatorio_api
        def verificar(*args, **kwargs):
            if papel_atual() not in papeis_aceitos:
                return jsonify({
                    "erro": "Você não tem permissão para esta ação."
                }), 403
            return rota(*args, **kwargs)

        return verificar

    return decorador


def tutor_obrigatorio_api(rota):
    @wraps(rota)
    @login_obrigatorio_api
    def verificar(*args, **kwargs):
        if not pode_ensinar():
            return jsonify({
                "erro": "Só quem tem permissão de tutor aprovada pode fazer isso."
            }), 403
        return rota(*args, **kwargs)

    return verificar


def admin_obrigatorio_api(rota):
    return papel_obrigatorio_api(PAPEL_ADMINISTRADOR)(rota)


def ensino_obrigatorio(rota):
    @wraps(rota)
    @login_obrigatorio
    def verificar(*args, **kwargs):
        if not pode_ensinar():
            return redirect(url_for("pagina.solicitarTutor"))
        return rota(*args, **kwargs)

    return verificar


def papel_obrigatorio(*papeis_aceitos):
    def decorador(rota):
        @wraps(rota)
        @login_obrigatorio
        def verificar(*args, **kwargs):
            if papel_atual() not in papeis_aceitos:
                return redirect(url_for("pagina.telaInicial"))
            return rota(*args, **kwargs)

        return verificar

    return decorador
