from flask import Flask

from config import Config
from routes.authRoutes import auth_bp
from routes.paginaRoutes import pagina_bp
from routes.turmaRoutes import turma_bp


def criar_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = Config.SECRET_KEY

    app.register_blueprint(pagina_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(turma_bp)

    return app


app = criar_app()


if __name__ == "__main__":
    app.run(debug=True)
