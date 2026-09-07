-- Migracao 008 - resolucao da questao
--
-- Rodar no Workbench com o script inteiro selecionado. Nao apaga dado.
--
-- Guarda a explicacao que o aluno ve depois de responder, principalmente
-- quando erra. E opcional: quem cadastra a questao decide se preenche.
--
-- Sem esta coluna, cadastrar qualquer questao pela tela da sala falha,
-- porque o INSERT passou a incluir "resolucao".

USE IFisica;

ALTER TABLE Exercicio
    ADD COLUMN resolucao TEXT NULL AFTER dificuldade;

-- Conferencia: deve aparecer 1 linha, coluna "resolucao".
SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'IFisica'
AND TABLE_NAME = 'Exercicio'
AND COLUMN_NAME = 'resolucao';
