CREATE DATABASE IF NOT EXISTS ifisica
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE ifisica;

CREATE TABLE IF NOT EXISTS Docente (
    idDocente INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    senhaHash VARCHAR(255) NOT NULL,
    contato VARCHAR(20),
    cpf VARCHAR(14) UNIQUE,
    dataNascimento DATE,
    naturalidade VARCHAR(80),
    origemDivulgacao VARCHAR(40),
    dataCadastro DATE NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS Turma (
    idTurma INT AUTO_INCREMENT PRIMARY KEY,
    nomeTurma VARCHAR(100) NOT NULL,
    descricao TEXT,
    dataCriacao DATE NOT NULL,
    idDocente INT NOT NULL,
    nivelEscolaridade VARCHAR(40),
    CONSTRAINT fk_turma_docente
        FOREIGN KEY (idDocente) REFERENCES Docente(idDocente)
        ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE INDEX idx_turma_docente ON Turma (idDocente);
