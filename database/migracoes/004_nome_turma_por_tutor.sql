-- Migracao 004 - nome de turma unico por tutor
--
-- Rodar depois da 003, com o script inteiro selecionado.
--
-- Hoje Turma.nome e UNIQUE global: dois tutores diferentes nao podem ter
-- turmas com o mesmo nome, e o segundo recebe um erro que nao explica nada.
-- Passa a ser unico por tutor: cada pessoa nao repete nome entre as proprias
-- turmas, mas "Fisica 2o ano" pode existir uma vez para cada tutor.
--
-- O indice novo entra antes de o antigo sair, mesma logica da 003.

USE IFisica;

ALTER TABLE Turma ADD UNIQUE KEY uq_turma_gerente_nome (idUsuarioGerente, nome);
ALTER TABLE Turma DROP INDEX nome;

-- Conferencia: uq_turma_gerente_nome com DUAS colunas (idUsuarioGerente, nome)
-- e nenhum indice unico so em nome.
SELECT INDEX_NAME, SEQ_IN_INDEX, COLUMN_NAME, NON_UNIQUE
FROM information_schema.STATISTICS
WHERE TABLE_SCHEMA = 'IFisica' AND TABLE_NAME = 'Turma'
ORDER BY INDEX_NAME, SEQ_IN_INDEX;
