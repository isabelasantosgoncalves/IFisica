from database.db import obter_cursor

DADOS = "idArquivo, nome, tipo, tamanho, idUsuario, dataEnvio"


def salvar(nome, tipo, conteudo, id_usuario):
    sql = """
        INSERT INTO Arquivo (nome, tipo, tamanho, conteudo, idUsuario)
        VALUES (%s, %s, %s, %s, %s)
    """

    with obter_cursor(commit=True) as cursor:
        cursor.execute(sql, (nome, tipo, len(conteudo), conteudo, id_usuario))
        return cursor.lastrowid


def buscar_conteudo(id_arquivo):
    sql = "SELECT nome, tipo, conteudo FROM Arquivo WHERE idArquivo = %s"

    with obter_cursor(dicionario=True) as cursor:
        cursor.execute(sql, (id_arquivo,))
        return cursor.fetchone()


def buscar_dados(id_arquivo):
    sql = f"SELECT {DADOS} FROM Arquivo WHERE idArquivo = %s"

    with obter_cursor(dicionario=True) as cursor:
        cursor.execute(sql, (id_arquivo,))
        return cursor.fetchone()
