-- Migracao 006 - Atividade.titulo -> Atividade.nome
-- O codigo em models/atividade.py sempre trabalhou com "nome"; o schema.sql
-- documentou a coluna como "titulo" e ninguem percebeu ate a criacao de
-- atividade comecar a falhar. Rodar uma vez, script inteiro.

USE IFisica;

ALTER TABLE Atividade CHANGE titulo nome VARCHAR(120) NOT NULL;

-- Conferencia: deve aparecer 1 linha, coluna "nome".
SELECT COLUMN_NAME FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'IFisica' AND TABLE_NAME = 'Atividade' AND COLUMN_NAME = 'nome';