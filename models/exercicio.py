from database.db import obter_cursor

COLUNAS = (
    "idExercicio", "pergunta",
    "alternativaA", "alternativaB", "alternativaC", "alternativaD",
    "alternativaCerta", "materia", "dificuldade", "resolucao", "imagem"
)

LISTA_COLUNAS = ", ".join(COLUNAS)


def criar(pergunta, alternativas, alternativa_certa, materia, dificuldade,
          resolucao=None, imagem=None):
    sql = """
        INSERT INTO Exercicio
        (pergunta, alternativaA, alternativaB, alternativaC, alternativaD,
         alternativaCerta, materia, dificuldade, resolucao, imagem)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    with obter_cursor(commit=True) as cursor:
        cursor.execute(sql, (
            pergunta,
            alternativas.get("A"), alternativas.get("B"),
            alternativas.get("C"), alternativas.get("D"),
            alternativa_certa, materia, dificuldade, resolucao, imagem
        ))
        return cursor.lastrowid


def listar(materia=None, dificuldade=None):
    sql = f"SELECT {LISTA_COLUNAS} FROM Exercicio WHERE 1=1"
    parametros = []

    if materia:
        sql += " AND materia = %s"
        parametros.append(materia)

    if dificuldade:
        sql += " AND dificuldade = %s"
        parametros.append(dificuldade)

    sql += " ORDER BY idExercicio DESC"

    with obter_cursor(dicionario=True) as cursor:
        cursor.execute(sql, tuple(parametros))
        return cursor.fetchall()


def buscar(id_exercicio):
    with obter_cursor(dicionario=True) as cursor:
        cursor.execute(
            f"SELECT {LISTA_COLUNAS} FROM Exercicio WHERE idExercicio = %s",
            (id_exercicio,)
        )
        return cursor.fetchone()


def atualizar(id_exercicio, pergunta, alternativas, alternativa_certa, materia,
              dificuldade, resolucao=None, imagem=None):
    sql = """
        UPDATE Exercicio
        SET pergunta = %s, alternativaA = %s, alternativaB = %s,
            alternativaC = %s, alternativaD = %s, alternativaCerta = %s,
            materia = %s, dificuldade = %s, resolucao = %s, imagem = %s
        WHERE idExercicio = %s
    """
    with obter_cursor(commit=True) as cursor:
        cursor.execute(sql, (
            pergunta,
            alternativas.get("A"), alternativas.get("B"),
            alternativas.get("C"), alternativas.get("D"),
            alternativa_certa, materia, dificuldade, resolucao, imagem,
            id_exercicio
        ))
        return cursor.rowcount > 0


def excluir(id_exercicio):
    with obter_cursor(commit=True) as cursor:
        cursor.execute(
            "DELETE FROM Exercicio WHERE idExercicio = %s",
            (id_exercicio,)
        )
        return cursor.rowcount > 0