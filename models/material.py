from database.db import obter_cursor

COLUNAS = """
    idMaterial, idTurma, assunto, titulo, descricao,
    tipo, url, arquivo, dataCriacao
"""

TIPO_LINK = "link"
TIPO_PDF = "pdf"

TIPOS = (TIPO_LINK, TIPO_PDF)


def criar(id_turma, assunto, titulo, descricao, tipo, url, arquivo):
    sql = """
        INSERT INTO Material
        (idTurma, assunto, titulo, descricao, tipo, url, arquivo)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    with obter_cursor(commit=True) as cursor:
        cursor.execute(sql, (id_turma, assunto, titulo, descricao, tipo, url, arquivo))
        return cursor.lastrowid


def listar_por_turma(id_turma):
    sql = f"""
        SELECT {COLUNAS}
        FROM Material
        WHERE idTurma = %s
        ORDER BY assunto, titulo
    """

    with obter_cursor(dicionario=True) as cursor:
        cursor.execute(sql, (id_turma,))
        return cursor.fetchall()


def buscar(id_material, id_turma):
    sql = f"""
        SELECT {COLUNAS}
        FROM Material
        WHERE idMaterial = %s AND idTurma = %s
    """

    with obter_cursor(dicionario=True) as cursor:
        cursor.execute(sql, (id_material, id_turma))
        return cursor.fetchone()


def atualizar(id_material, id_turma, assunto, titulo, descricao, tipo, url, arquivo):
    sql = """
        UPDATE Material
        SET assunto = %s, titulo = %s, descricao = %s,
            tipo = %s, url = %s, arquivo = %s
        WHERE idMaterial = %s AND idTurma = %s
    """

    with obter_cursor(commit=True) as cursor:
        cursor.execute(sql, (
            assunto, titulo, descricao, tipo, url, arquivo, id_material, id_turma
        ))
        return cursor.rowcount


def excluir(id_material, id_turma):
    sql = "DELETE FROM Material WHERE idMaterial = %s AND idTurma = %s"

    with obter_cursor(commit=True) as cursor:
        cursor.execute(sql, (id_material, id_turma))
        return cursor.rowcount
