-- Migracao 002 - e-mail unico de verdade
--
-- Rodar depois da 001, com o script inteiro selecionado.
--
-- Hoje Usuario tem UNIQUE (email, telefone) - um indice composto.
-- Na pratica isso permite o MESMO e-mail se cadastrar varias vezes, bastando
-- um telefone diferente. O login busca por e-mail e passaria a ter ambiguidade.
--
-- Os indices novos entram ANTES de o antigo sair, para a tabela nunca ficar
-- um instante sem restricao.

USE IFisica;

ALTER TABLE Usuario ADD UNIQUE KEY uq_usuario_email (email);
ALTER TABLE Usuario ADD UNIQUE KEY uq_usuario_telefone (telefone);
ALTER TABLE Usuario DROP INDEX email;

-- Conferencia: uq_usuario_email e uq_usuario_telefone, cada um com UMA coluna,
-- e nenhum indice chamado "email".
SELECT INDEX_NAME, SEQ_IN_INDEX, COLUMN_NAME, NON_UNIQUE
FROM information_schema.STATISTICS
WHERE TABLE_SCHEMA = 'IFisica' AND TABLE_NAME = 'Usuario'
ORDER BY INDEX_NAME, SEQ_IN_INDEX;
