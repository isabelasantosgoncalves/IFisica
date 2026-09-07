from flask import Blueprint, Response, jsonify, request, session

from models import arquivo as modelo_arquivo
from routes.seguranca import login_obrigatorio_api, tutor_obrigatorio_api

upload_bp = Blueprint("upload", __name__)

TIPOS_IMAGEM = ("image/jpeg", "image/png", "image/gif", "image/webp")

TAMANHO_MAXIMO_IMAGEM = 3 * 1024 * 1024
TAMANHO_MAXIMO_PDF = 10 * 1024 * 1024

ASSINATURAS_IMAGEM = (
    (b"\xff\xd8\xff", "image/jpeg"),
    (b"\x89PNG\r\n\x1a\n", "image/png"),
    (b"GIF87a", "image/gif"),
    (b"GIF89a", "image/gif")
)


def tipo_real_da_imagem(conteudo):
    """A extensão e o tipo que o navegador informa podem mentir; os primeiros
    bytes do arquivo, não."""
    for assinatura, tipo in ASSINATURAS_IMAGEM:
        if conteudo.startswith(assinatura):
            return tipo

    if conteudo[:4] == b"RIFF" and conteudo[8:12] == b"WEBP":
        return "image/webp"

    return None


def ler_enviado(campo):
    arquivo = request.files.get(campo)

    if not arquivo or not arquivo.filename:
        return None, None

    return arquivo.read(), arquivo.filename[:160]


@upload_bp.route("/uploads/exercicios", methods=["POST"])
@tutor_obrigatorio_api
def enviar_imagem():

    conteudo, nome = ler_enviado("imagem")

    if not conteudo:
        return jsonify({"erro": "Escolha uma imagem."}), 400

    if len(conteudo) > TAMANHO_MAXIMO_IMAGEM:
        return jsonify({"erro": "A imagem precisa ter no máximo 3 MB."}), 400

    tipo = tipo_real_da_imagem(conteudo)

    if tipo not in TIPOS_IMAGEM:
        return jsonify({
            "erro": "Esse arquivo não parece ser uma imagem JPG, PNG, GIF ou WEBP."
        }), 400

    id_arquivo = modelo_arquivo.salvar(nome, tipo, conteudo, session["idUsuario"])

    return jsonify({
        "mensagem": "Imagem enviada!",
        "idArquivo": id_arquivo,
        "url": f"/api/arquivos/{id_arquivo}"
    }), 201


@upload_bp.route("/uploads/materiais", methods=["POST"])
@tutor_obrigatorio_api
def enviar_pdf():

    conteudo, nome = ler_enviado("arquivo")

    if not conteudo:
        return jsonify({"erro": "Escolha um arquivo PDF."}), 400

    if len(conteudo) > TAMANHO_MAXIMO_PDF:
        return jsonify({"erro": "O PDF precisa ter no máximo 10 MB."}), 400

    if not conteudo.startswith(b"%PDF-"):
        return jsonify({"erro": "Esse arquivo não parece ser um PDF."}), 400

    id_arquivo = modelo_arquivo.salvar(
        nome, "application/pdf", conteudo, session["idUsuario"]
    )

    return jsonify({
        "mensagem": "PDF enviado!",
        "idArquivo": id_arquivo,
        "url": f"/api/arquivos/{id_arquivo}"
    }), 201


@upload_bp.route("/arquivos/<int:id_arquivo>", methods=["GET"])
@login_obrigatorio_api
def baixar(id_arquivo):

    arquivo = modelo_arquivo.buscar_conteudo(id_arquivo)

    if not arquivo:
        return jsonify({"erro": "Arquivo não encontrado."}), 404

    resposta = Response(arquivo["conteudo"], mimetype=arquivo["tipo"])
    resposta.headers["Content-Disposition"] = (
        f'inline; filename="{arquivo["nome"]}"'
    )
    resposta.headers["Cache-Control"] = "private, max-age=86400"

    return resposta
