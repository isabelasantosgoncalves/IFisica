-- Migracao 005 - tipo com padrao e codigo de convite da sala
--
-- Ja foi aplicada no servidor por um script Python avulso; este arquivo
-- existe para o repositorio ter o historico completo em SQL, e para quem
-- montar o banco do zero conseguir chegar no mesmo estado.
--
-- Rodar uma vez, script inteiro. Nao apaga dado.

USE IFisica;

ALTER TABLE Turma
    MODIFY tipo VARCHAR(20) NOT NULL DEFAULT 'Regular';

ALTER TABLE Turma
    ADD COLUMN codigoConvite VARCHAR(8) NULL AFTER tipo;

ALTER TABLE Turma
    ADD UNIQUE KEY uq_turma_codigo_convite (codigoConvite);

-- Conferencia: duas linhas, tipo e codigoConvite.
SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_DEFAULT
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'IFisica' AND TABLE_NAME = 'Turma'
AND COLUMN_NAME IN ('tipo', 'codigoConvite');
