from database.db import obter_cursor


def atualizar_dados(id_usuario, nome, telefone, genero, genero_autodeclarado):
    sql = """
        UPDATE Usuario
        SET nome = %s, telefone = %s,
            genero = %s, generoAutodeclarado = %s
        WHERE idUsuario = %s
    """

    with obter_cursor(commit=True) as cursor:
        cursor.execute(sql, (
            nome, telefone, genero, genero_autodeclarado, id_usuario
        ))
        return cursor.rowcount


def buscar_senha(id_usuario):
    sql = "SELECT senha FROM Usuario WHERE idUsuario = %s"

    with obter_cursor(dicionario=True) as cursor:
        cursor.execute(sql, (id_usuario,))
        linha = cursor.fetchone()
        return linha["senha"] if linha else None


def atualizar_senha(id_usuario, senha_hash):
    sql = "UPDATE Usuario SET senha = %s WHERE idUsuario = %s"

    with obter_cursor(commit=True) as cursor:
        cursor.execute(sql, (senha_hash, id_usuario))
        return cursor.rowcount
