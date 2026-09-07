-- Migracao 009 - imagem opcional na questao
--
-- Rodar depois da 008, no Workbench, script inteiro. Nao apaga dado.
--
-- Guarda apenas o NOME do arquivo salvo em static/uploads/exercicios.
-- O arquivo em si fica no disco do servidor, nao no banco: imagem em
-- coluna BLOB incha o banco e deixa toda consulta mais lenta.
--
-- E opcional: quem cadastra a questao decide se manda imagem ou nao.

USE IFisica;

ALTER TABLE Exercicio
    ADD COLUMN imagem VARCHAR(120) NULL AFTER resolucao;

-- Conferencia: deve aparecer 1 linha, coluna "imagem".
SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'IFisica'
AND TABLE_NAME = 'Exercicio'
AND COLUMN_NAME = 'imagem';
