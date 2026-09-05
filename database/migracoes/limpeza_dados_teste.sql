-- Limpeza dos dados de teste criados durante a verificacao
--
-- Rodar no Workbench com o script INTEIRO selecionado (o raio da barra).
-- Deixa o banco vazio de novo.
--
-- Apaga APENAS as contas de teste (e-mails @exemplo.com) e tudo que
-- pendura nelas. Nenhuma conta real e tocada.
--
-- SOBRE O SET SQL_SAFE_UPDATES:
-- o Workbench vem com "safe update mode" ligado, que recusa DELETE cujo
-- WHERE nao filtra direto por chave primaria (erro 1175). Como aqui o filtro
-- e por subconsulta, precisamos desligar durante o script e religar no fim.
-- Vale so para esta conexao e estas linhas.
--
-- A ORDEM IMPORTA, por causa das chaves estrangeiras:
--   Turma aponta para Solicitacao e para Usuario
--   Solicitacao aponta para Admin e para Usuario
--   Admin aponta para Usuario
-- Entao: Turma -> Solicitacao -> Admin -> Usuario.

USE IFisica;

SET SQL_SAFE_UPDATES = 0;

-- Confira o que vai sumir. Devem aparecer so contas @exemplo.com.
SELECT idUsuario, nome, email FROM Usuario WHERE email LIKE '%@exemplo.com';

DROP TEMPORARY TABLE IF EXISTS alvo;

CREATE TEMPORARY TABLE alvo AS
SELECT idUsuario FROM Usuario WHERE email LIKE '%@exemplo.com';

DELETE FROM Turma       WHERE idUsuarioGerente IN (SELECT idUsuario FROM alvo);
DELETE FROM Solicitacao WHERE idUsuario        IN (SELECT idUsuario FROM alvo);
DELETE FROM Admin       WHERE idUsuario        IN (SELECT idUsuario FROM alvo);
DELETE FROM Usuario     WHERE idUsuario        IN (SELECT idUsuario FROM alvo);

DROP TEMPORARY TABLE alvo;

SET SQL_SAFE_UPDATES = 1;

-- Conferencia: as quatro contagens devem voltar zero.
SELECT 'Usuario'     AS tabela, COUNT(*) AS linhas FROM Usuario
UNION ALL SELECT 'Admin',       COUNT(*) FROM Admin
UNION ALL SELECT 'Solicitacao', COUNT(*) FROM Solicitacao
UNION ALL SELECT 'Turma',       COUNT(*) FROM Turma;
