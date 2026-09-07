import os
import secrets

from flask import Blueprint, current_app, jsonify, request

from routes.seguranca import tutor_obrigatorio_api

upload_bp = Blueprint("upload", __name__)

PASTA_EXERCICIOS = os.path.join("static", "uploads", "exercicios")
PASTA_MATERIAIS = os.path.join("static", "uploads", "materiais")

EXTENSOES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp"
}

TAMANHO_MAXIMO = 3 * 1024 * 1024
TAMANHO_MAXIMO_PDF = 10 * 1024 * 1024

ASSINATURAS = (
    (b"\xff\xd8\xff", ".jpg"),
    (b"\x89PNG\r\n\x1a\n", ".png"),
    (b"GIF87a", ".gif"),
    (b"GIF89a", ".gif"),
)


def extensao_confiavel(arquivo):
    inicio = arquivo.read(16)
    arquivo.seek(0)

    for assinatura, extensao in ASSINATURAS:
        if inicio.startswith(assinatura):
            return extensao

    if inicio[:4] == b"RIFF" and inicio[8:12] == b"WEBP":
        return ".webp"

    return None


@upload_bp.route("/uploads/exercicios", methods=["POST"])
@tutor_obrigatorio_api
def enviar_imagem():

    arquivo = request.files.get("imagem")

    if not arquivo or not arquivo.filename:
        return jsonify({"erro": "Escolha uma imagem."}), 400

    if arquivo.mimetype not in EXTENSOES:
        return jsonify({
            "erro": "A imagem precisa ser JPG, PNG, GIF ou WEBP."
        }), 400

    arquivo.seek(0, os.SEEK_END)
    tamanho = arquivo.tell()
    arquivo.seek(0)

    if tamanho > TAMANHO_MAXIMO:
        return jsonify({
            "erro": "A imagem precisa ter no máximo 3 MB."
        }), 400

    extensao = extensao_confiavel(arquivo)

    if not extensao:
        return jsonify({
            "erro": "Esse arquivo não parece ser uma imagem."
        }), 400

    nome = secrets.token_hex(16) + extensao
    destino = os.path.join(current_app.root_path, PASTA_EXERCICIOS)

    os.makedirs(destino, exist_ok=True)
    arquivo.save(os.path.join(destino, nome))

    return jsonify({
        "mensagem": "Imagem enviada!",
        "imagem": nome,
        "url": f"/static/uploads/exercicios/{nome}"
    }), 201


def medir(arquivo):
    arquivo.seek(0, os.SEEK_END)
    tamanho = arquivo.tell()
    arquivo.seek(0)
    return tamanho


@upload_bp.route("/uploads/materiais", methods=["POST"])
@tutor_obrigatorio_api
def enviar_pdf():

    arquivo = request.files.get("arquivo")

    if not arquivo or not arquivo.filename:
        return jsonify({"erro": "Escolha um arquivo PDF."}), 400

    if medir(arquivo) > TAMANHO_MAXIMO_PDF:
        return jsonify({"erro": "O PDF precisa ter no máximo 10 MB."}), 400

    inicio = arquivo.read(5)
    arquivo.seek(0)

    if inicio != b"%PDF-":
        return jsonify({"erro": "Esse arquivo não parece ser um PDF."}), 400

    nome = secrets.token_hex(16) + ".pdf"
    destino = os.path.join(current_app.root_path, PASTA_MATERIAIS)

    os.makedirs(destino, exist_ok=True)
    arquivo.save(os.path.join(destino, nome))

    return jsonify({
        "mensagem": "PDF enviado!",
        "arquivo": nome,
        "url": f"/static/uploads/materiais/{nome}"
    }), 201
