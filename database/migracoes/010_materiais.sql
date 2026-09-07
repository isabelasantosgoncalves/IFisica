-- Migracao 010 - materiais de estudo da sala
--
-- Rodar no Workbench com o script inteiro selecionado. Nao apaga dado.
--
-- Guarda link ou PDF que o tutor disponibiliza para a sala, agrupado por
-- assunto. No caso do PDF, aqui fica so o NOME do arquivo salvo em
-- static/uploads/materiais - o arquivo em si fica no disco.

USE IFisica;

CREATE TABLE IF NOT EXISTS Material (
    idMaterial INT NOT NULL AUTO_INCREMENT,
    idTurma INT NOT NULL,
    assunto VARCHAR(100) NOT NULL,
    titulo VARCHAR(120) NOT NULL,
    descricao VARCHAR(255) NULL,
    tipo VARCHAR(10) NOT NULL,
    url VARCHAR(500) NULL,
    arquivo VARCHAR(120) NULL,
    dataCriacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (idMaterial),
    KEY idx_material_turma (idTurma),
    KEY idx_material_assunto (idTurma, assunto),

    CONSTRAINT fk_material_turma FOREIGN KEY (idTurma)
        REFERENCES Turma(idTurma) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Conferencia: deve aparecer a tabela Material.
SELECT TABLE_NAME FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'IFisica' AND TABLE_NAME = 'Material';
