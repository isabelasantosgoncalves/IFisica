SOLICITACAO_PENDENTE = 0
SOLICITACAO_APROVADA = 1
SOLICITACAO_RECUSADA = 2

ROTULOS_STATUS = {
    SOLICITACAO_PENDENTE: "Aguardando aprovação",
    SOLICITACAO_APROVADA: "Aprovada",
    SOLICITACAO_RECUSADA: "Recusada"
}

PAPEL_ESTUDANTE = "estudante"
PAPEL_TUTOR = "tutor"
PAPEL_ADMINISTRADOR = "administrador"

NIVEIS = (
    (1, "1º ano de E.M"),
    (2, "2º ano de E.M"),
    (3, "3º ano de E.M"),
    (4, "Pré-Vestibular"),
    (5, "Ensino superior")
)

CODIGOS_NIVEL = {codigo for codigo, _ in NIVEIS}

ROTULOS_NIVEL = dict(NIVEIS)

GENEROS = (
    ("mulher_cis", "Mulher cis"),
    ("homem_cis", "Homem cis"),
    ("mulher_trans", "Mulher trans"),
    ("homem_trans", "Homem trans"),
    ("nao_binarie", "Não-binárie"),
    ("genero_fluido", "Gênero fluido"),
    ("agenero", "Agênero"),
    ("bigenero", "Bigênero"),
    ("genero_neutro", "Gênero neutro"),
    ("autodeclaracao", "Prefiro me autodeclarar"),
    ("nao_informar", "Prefiro não informar")
)

CODIGOS_GENERO = {codigo for codigo, _ in GENEROS}

GENERO_AUTODECLARACAO = "autodeclaracao"

NIVEIS_ALUNO = (
    (0, "Iniciante"),
    (10, "Aprendiz"),
    (25, "Praticante"),
    (50, "Avançado"),
    (100, "Mestre"),
    (200, "Lenda da Física")
)
