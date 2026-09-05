-- Conferencia das migracoes 001 a 004
--
-- So leitura: nenhum comando aqui altera nada.
-- Devolve UM unico resultado, uma linha por verificacao.
-- Todas as linhas devem estar com situacao = OK.
--
-- Sao 9 colunas com AUTO_INCREMENT, e nao 8: a migracao 001 mexeu em oito,
-- mas Resposta.idResposta ja vinha assim do banco original.

USE IFisica;

SELECT * FROM (

    SELECT 1 AS ordem,
           '001 - colunas com AUTO_INCREMENT' AS verificacao,
           '9' AS esperado,
           CAST(COUNT(*) AS CHAR) AS encontrado,
           IF(COUNT(*) = 9, 'OK', 'FALTA') AS situacao
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = 'IFisica' AND EXTRA LIKE '%auto_increment%'

    UNION ALL SELECT 2,
           '002 - indice unico so em Usuario.email', '1',
           CAST(COUNT(*) AS CHAR),
           IF(COUNT(*) = 1, 'OK', 'FALTA')
    FROM information_schema.STATISTICS
    WHERE TABLE_SCHEMA = 'IFisica' AND TABLE_NAME = 'Usuario'
      AND INDEX_NAME = 'uq_usuario_email'

    UNION ALL SELECT 3,
           '002 - indice unico so em Usuario.telefone', '1',
           CAST(COUNT(*) AS CHAR),
           IF(COUNT(*) = 1, 'OK', 'FALTA')
    FROM information_schema.STATISTICS
    WHERE TABLE_SCHEMA = 'IFisica' AND TABLE_NAME = 'Usuario'
      AND INDEX_NAME = 'uq_usuario_telefone'

    UNION ALL SELECT 4,
           '002 - indice composto antigo removido', '0',
           CAST(COUNT(*) AS CHAR),
           IF(COUNT(*) = 0, 'OK', 'AINDA EXISTE')
    FROM information_schema.STATISTICS
    WHERE TABLE_SCHEMA = 'IFisica' AND TABLE_NAME = 'Usuario'
      AND INDEX_NAME = 'email'

    UNION ALL SELECT 5,
           '003 - genero e generoAutodeclarado em Usuario', '2',
           CAST(COUNT(*) AS CHAR),
           IF(COUNT(*) = 2, 'OK', 'FALTA')
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = 'IFisica' AND TABLE_NAME = 'Usuario'
      AND COLUMN_NAME IN ('genero', 'generoAutodeclarado')

    UNION ALL SELECT 6,
           '003 - conteudo, publicoAlvo e dataDecisao', '3',
           CAST(COUNT(*) AS CHAR),
           IF(COUNT(*) = 3, 'OK', 'FALTA')
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = 'IFisica' AND TABLE_NAME = 'Solicitacao'
      AND COLUMN_NAME IN ('conteudo', 'publicoAlvo', 'dataDecisao')

    UNION ALL SELECT 7,
           '003 - Turma.idSolicitacao virou indice comum', '1',
           CAST(COUNT(*) AS CHAR),
           IF(COUNT(*) = 1, 'OK', 'FALTA')
    FROM information_schema.STATISTICS
    WHERE TABLE_SCHEMA = 'IFisica' AND TABLE_NAME = 'Turma'
      AND INDEX_NAME = 'idx_turma_solicitacao' AND NON_UNIQUE = 1

    UNION ALL SELECT 8,
           '003 - UNIQUE antigo de idSolicitacao removido', '0',
           CAST(COUNT(*) AS CHAR),
           IF(COUNT(*) = 0, 'OK', 'AINDA EXISTE')
    FROM information_schema.STATISTICS
    WHERE TABLE_SCHEMA = 'IFisica' AND TABLE_NAME = 'Turma'
      AND INDEX_NAME = 'idSolicitacao'

    UNION ALL SELECT 9,
           '004 - nome unico por tutor (2 colunas)', '2',
           CAST(COUNT(*) AS CHAR),
           IF(COUNT(*) = 2, 'OK', 'FALTA')
    FROM information_schema.STATISTICS
    WHERE TABLE_SCHEMA = 'IFisica' AND TABLE_NAME = 'Turma'
      AND INDEX_NAME = 'uq_turma_gerente_nome'

    UNION ALL SELECT 10,
           '004 - UNIQUE global de Turma.nome removido', '0',
           CAST(COUNT(*) AS CHAR),
           IF(COUNT(*) = 0, 'OK', 'AINDA EXISTE')
    FROM information_schema.STATISTICS
    WHERE TABLE_SCHEMA = 'IFisica' AND TABLE_NAME = 'Turma'
      AND INDEX_NAME = 'nome'

    UNION ALL SELECT 11,
           'chaves estrangeiras intactas', '18',
           CAST(COUNT(*) AS CHAR),
           IF(COUNT(*) = 18, 'OK', 'CONFERIR')
    FROM information_schema.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA = 'IFisica' AND REFERENCED_TABLE_NAME IS NOT NULL

) AS conferencia
ORDER BY ordem;
