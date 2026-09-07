from flask import Flask

from config import Config, conferir_configuracao
from routes.authRoutes import auth_bp
from routes.paginaRoutes import pagina_bp
from routes.solicitacaoRoutes import solicitacao_bp
from routes.turmaRoutes import turma_bp
from routes.atividadeRoutes import atividade_bp
from routes.salaRoutes import sala_bp
from routes.exercicioRoutes import exercicio_bp
from routes.respostaRoutes import resposta_bp
from routes.desempenhoRoutes import desempenho_bp
from routes.materialRoutes import material_bp
from routes.uploadRoutes import upload_bp


def criar_app():
    conferir_configuracao()

    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = Config.SECRET_KEY

    app.register_blueprint(exercicio_bp, url_prefix="/api")
    app.register_blueprint(pagina_bp)
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(turma_bp, url_prefix="/api")
    app.register_blueprint(solicitacao_bp, url_prefix="/api")
    app.register_blueprint(atividade_bp, url_prefix="/api")
    app.register_blueprint(sala_bp, url_prefix="/api")
    app.register_blueprint(resposta_bp, url_prefix="/api")
    app.register_blueprint(upload_bp, url_prefix="/api")
    app.register_blueprint(material_bp, url_prefix="/api")
    app.register_blueprint(desempenho_bp, url_prefix="/api")

    return app


app = criar_app()


if __name__ == "__main__":
    app.run(debug=True)
