from flask import Flask

from config import Config, conferir_configuracao
from routes.authRoutes import auth_bp
from routes.paginaRoutes import pagina_bp
from routes.solicitacaoRoutes import solicitacao_bp
from routes.turmaRoutes import turma_bp


def criar_app():
    conferir_configuracao()

    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = Config.SECRET_KEY

    app.register_blueprint(pagina_bp)
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(turma_bp, url_prefix="/api")
    app.register_blueprint(solicitacao_bp, url_prefix="/api")

    return app


app = criar_app()


if __name__ == "__main__":
    app.run(debug=True)
