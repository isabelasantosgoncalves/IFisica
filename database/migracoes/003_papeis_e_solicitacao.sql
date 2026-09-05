-- Migracao 003 - colunas que as funcionalidades de contas e permissoes exigem
--
-- Rodar depois da 002, com o script inteiro selecionado.
-- Nenhum comando aqui apaga dado.

USE IFisica;

-- 1. Genero com autodeclaracao no cadastro.
--    Duas colunas: a opcao escolhida e o texto livre de quem se autodeclara.
--    Ambas opcionais, porque "prefiro nao informar" e uma resposta valida.
ALTER TABLE Usuario ADD COLUMN genero VARCHAR(60) NULL AFTER dataNasc;
ALTER TABLE Usuario ADD COLUMN generoAutodeclarado VARCHAR(120) NULL AFTER genero;

-- 2. O formulario de solicitacao de tutor pede motivo, conteudo que pretende
--    ensinar e publico-alvo. So o motivo existe hoje.
ALTER TABLE Solicitacao ADD COLUMN conteudo VARCHAR(255) NULL AFTER motivo;
ALTER TABLE Solicitacao ADD COLUMN publicoAlvo VARCHAR(255) NULL AFTER conteudo;

-- 3. Data da decisao do administrador, para o painel saber quando foi analisada.
ALTER TABLE Solicitacao ADD COLUMN dataDecisao DATE NULL AFTER status;

-- 4. Turma.idSolicitacao e UNIQUE hoje. Como a solicitacao e o pedido de
--    permissao de tutor (uma por pessoa), o UNIQUE faz cada tutor poder criar
--    UMA turma na vida. Trocar por indice comum resolve, sem perder o vinculo.
--
--    A ordem importa: idSolicitacao e coluna de chave estrangeira, e o MySQL
--    exige que exista um indice sobre ela. Se o UNIQUE saisse primeiro, a
--    tabela ficaria sem indice e o comando seria recusado (erro 1553).
--    Por isso o indice novo entra ANTES de o antigo sair.
ALTER TABLE Turma ADD INDEX idx_turma_solicitacao (idSolicitacao);
ALTER TABLE Turma DROP INDEX idSolicitacao;

-- Conferencia 1: Usuario com genero e generoAutodeclarado;
-- Solicitacao com conteudo, publicoAlvo e dataDecisao.
SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'IFisica' AND TABLE_NAME IN ('Usuario', 'Solicitacao')
ORDER BY TABLE_NAME, ORDINAL_POSITION;

-- Conferencia 2: idx_turma_solicitacao com NON_UNIQUE = 1,
-- e nenhum indice chamado idSolicitacao.
SELECT INDEX_NAME, SEQ_IN_INDEX, COLUMN_NAME, NON_UNIQUE
FROM information_schema.STATISTICS
WHERE TABLE_SCHEMA = 'IFisica' AND TABLE_NAME = 'Turma'
ORDER BY INDEX_NAME, SEQ_IN_INDEX;
