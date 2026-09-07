-- Limpeza dos dados de teste criados durante a verificacao
--
-- Rodar no Workbench com o script INTEIRO selecionado (o raio da barra).
--
-- Apaga APENAS as contas de teste (e-mails @exemplo.com) e tudo que
-- pendura nelas. Contas reais e a conta admin@gmail.com nao sao tocadas.
--
-- SOBRE O SET SQL_SAFE_UPDATES: o Workbench recusa DELETE cujo WHERE nao
-- filtra direto por chave primaria (erro 1175). Desligamos durante o script
-- e religamos no fim. Vale so para esta conexao.
--
-- A ORDEM IMPORTA por causa das chaves estrangeiras: primeiro o que aponta
-- para a atividade e para a turma, depois a turma, depois o usuario.

USE IFisica;

SET SQL_SAFE_UPDATES = 0;

-- Confira o que vai sumir. Devem aparecer so contas @exemplo.com.
SELECT idUsuario, nome, email FROM Usuario WHERE email LIKE '%@exemplo.com';

DROP TEMPORARY TABLE IF EXISTS alvo;

CREATE TEMPORARY TABLE alvo AS
SELECT idUsuario FROM Usuario WHERE email LIKE '%@exemplo.com';

DROP TEMPORARY TABLE IF EXISTS turmas_alvo;

CREATE TEMPORARY TABLE turmas_alvo AS
SELECT idTurma FROM Turma
WHERE idUsuarioGerente IN (SELECT idUsuario FROM alvo);

DELETE FROM RespostaAtividade
WHERE idRealizacao IN (
    SELECT idRealizacao FROM (
        SELECT idRealizacao FROM RealizacaoAtividade
        WHERE idUsuario IN (SELECT idUsuario FROM alvo)
    ) AS r
);

DELETE FROM RealizacaoAtividade
WHERE idUsuario IN (SELECT idUsuario FROM alvo);

DELETE FROM AtividadeExercicio
WHERE idAtividade IN (
    SELECT idAtividade FROM (
        SELECT idAtividade FROM Atividade
        WHERE idTurma IN (SELECT idTurma FROM turmas_alvo)
    ) AS a
);

DELETE FROM Atividade
WHERE idTurma IN (SELECT idTurma FROM turmas_alvo);

DELETE FROM Participacao
WHERE idUsuario IN (SELECT idUsuario FROM alvo)
   OR idTurma IN (SELECT idTurma FROM turmas_alvo);

DELETE FROM SolicitacaoEntrada
WHERE idUsuario IN (SELECT idUsuario FROM alvo)
   OR idTurma IN (SELECT idTurma FROM turmas_alvo);

DELETE FROM Turma WHERE idTurma IN (SELECT idTurma FROM turmas_alvo);

DELETE FROM Solicitacao WHERE idUsuario IN (SELECT idUsuario FROM alvo);
DELETE FROM Admin       WHERE idUsuario IN (SELECT idUsuario FROM alvo);
DELETE FROM Usuario     WHERE idUsuario IN (SELECT idUsuario FROM alvo);

DROP TEMPORARY TABLE turmas_alvo;
DROP TEMPORARY TABLE alvo;

SET SQL_SAFE_UPDATES = 1;

-- Conferencia: nenhuma conta @exemplo.com deve sobrar.
SELECT COUNT(*) AS contas_de_teste_restantes
FROM Usuario WHERE email LIKE '%@exemplo.com';
