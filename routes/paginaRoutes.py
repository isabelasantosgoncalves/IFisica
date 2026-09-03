from flask import Blueprint, redirect, render_template, session, url_for

from routes.seguranca import docente_logado, login_obrigatorio

pagina_bp = Blueprint("pagina", __name__)

NIVEIS_ESCOLARIDADE = [
    "1º ano de E.M",
    "2º ano de E.M",
    "3º ano de E.M",
    "Pré-Vestibular",
    "Ensino superior"
]

ORIGENS = [
    ("Outros professores", "https://www.pngkey.com/png/detail/587-5870729_graphic-royalty-free-stock-teacher-excellence-day-care.png", 100),
    ("Alunos", "https://tse1.mm.bing.net/th/id/OIP.N6Phgg_Ftypdrhy5wYdzTQHaHF?rs=1&pid=ImgDetMain&o=7&rm=3", 105),
    ("Redes sociais", "https://tse2.mm.bing.net/th/id/OIP.oqhLnjoyZt1zzM_979gxmAHaHa?rs=1&pid=ImgDetMain&o=7&rm=3", 100),
    ("Busca na internet", "https://img.freepik.com/vetores-premium/tecnologia-de-conexao-de-rede-de-internet-intranet-em-ilustracao-plana-de-desenhos-animados-mao-desenhada-modelo_2175-7758.jpg?w=1480", 150),
    ("Notícias", "https://img.freepik.com/vetores-premium/criancas-desenhando-desenho-animado-ilustracao-vetorial-icone-de-jornal-isolado-em-fundo-branco_760559-1300.jpg", 100),
    ("Outros...", "https://i.pinimg.com/originals/2d/38/19/2d3819178273ab7fa24dc3c0f508203d.png", 100)
]


@pagina_bp.route("/")
def index():
    if docente_logado():
        return redirect(url_for("pagina.telaInicial"))
    return render_template("index.html")


@pagina_bp.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")


@pagina_bp.route("/login")
def login():
    return render_template("login.html")


@pagina_bp.route("/inicio")
@login_obrigatorio
def telaInicial():
    return render_template("telaInicial.html", nome=session.get("nomeDocente"))


@pagina_bp.route("/nova-turma")
@login_obrigatorio
def novaTurma():
    return render_template("turma.html")


@pagina_bp.route("/nova-turma/escolaridade")
@login_obrigatorio
def escolaridade():
    return render_template("escolaridade.html", niveis=NIVEIS_ESCOLARIDADE)


@pagina_bp.route("/nova-turma/origem")
@login_obrigatorio
def origem():
    return render_template("encontrou.html", origens=ORIGENS)
