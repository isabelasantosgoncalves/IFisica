from functools import wraps

from flask import jsonify, redirect, session, url_for


def docente_logado():
    return session.get("idDocente")


def login_obrigatorio(rota):
    @wraps(rota)
    def verificar(*args, **kwargs):
        if not docente_logado():
            return redirect(url_for("pagina.login"))
        return rota(*args, **kwargs)

    return verificar


def login_obrigatorio_api(rota):
    @wraps(rota)
    def verificar(*args, **kwargs):
        if not docente_logado():
            return jsonify({"erro": "Sessão expirada. Faça login novamente."}), 401
        return rota(*args, **kwargs)

    return verificar
