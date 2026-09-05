-- Migracao 001 - chaves primarias auto incrementais
--
-- Rodar UMA vez no banco IFisica, pelo MySQL Workbench, com o script INTEIRO
-- selecionado (o raio de "Execute"), nao linha por linha.
-- Seguro agora: o banco esta vazio (zero linhas em todas as tabelas).
--
-- Sem isto, todo INSERT precisa informar o id na mao e cursor.lastrowid
-- nao devolve nada, o que quebra cadastro de usuario e criacao de turma.
--
-- Nao apaga dado nenhum: so muda o comportamento do id ao inserir.
--
-- POR QUE O SET FOREIGN_KEY_CHECKS:
-- o MySQL recusa ALTER numa coluna apontada por chave estrangeira, mesmo
-- quando o tipo continua o mesmo (erro 1833). Desligar a checagem durante o
-- script e religar no fim resolve. O efeito e so desta conexao e destas
-- linhas: nenhuma chave estrangeira e removida, e no fim tudo volta ao normal.
-- Por isso o script tem que rodar inteiro de uma vez, na mesma aba.

USE IFisica;

SET FOREIGN_KEY_CHECKS = 0;

ALTER TABLE Usuario            MODIFY idUsuario            INT NOT NULL AUTO_INCREMENT;
ALTER TABLE Solicitacao        MODIFY idSolicitacao        INT NOT NULL AUTO_INCREMENT;
ALTER TABLE Turma              MODIFY idTurma              INT NOT NULL AUTO_INCREMENT;
ALTER TABLE SolicitacaoEntrada MODIFY idSolicitacaoEntrada INT NOT NULL AUTO_INCREMENT;
ALTER TABLE Exercicio          MODIFY idExercicio          INT NOT NULL AUTO_INCREMENT;
ALTER TABLE Lista              MODIFY idLista              INT NOT NULL AUTO_INCREMENT;
ALTER TABLE RealizarLista      MODIFY idRealizacao         INT NOT NULL AUTO_INCREMENT;
ALTER TABLE Ranking            MODIFY idRanking            INT NOT NULL AUTO_INCREMENT;

SET FOREIGN_KEY_CHECKS = 1;

-- Conferencia: tem que listar as OITO colunas acima com auto_increment.
SELECT TABLE_NAME, COLUMN_NAME, EXTRA
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'IFisica' AND EXTRA LIKE '%auto_increment%'
ORDER BY TABLE_NAME;
