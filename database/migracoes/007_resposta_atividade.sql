USE IFisica;

CREATE TABLE IF NOT EXISTS RealizacaoAtividade (
    idRealizacao INT NOT NULL AUTO_INCREMENT,
    idAtividade INT NOT NULL,
    idUsuario INT NOT NULL,
    dataRealizacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    pontuacao INT DEFAULT NULL,
    totalQuestoes INT DEFAULT NULL,

    PRIMARY KEY (idRealizacao),
    UNIQUE KEY uq_realizacao_atividade_usuario (idAtividade, idUsuario),
    KEY idUsuario (idUsuario),

    CONSTRAINT fk_realizacao_atividade FOREIGN KEY (idAtividade)
        REFERENCES Atividade(idAtividade) ON DELETE CASCADE,
    CONSTRAINT fk_realizacao_usuario FOREIGN KEY (idUsuario)
        REFERENCES Usuario(idUsuario)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS RespostaAtividade (
    idRespostaAtividade INT NOT NULL AUTO_INCREMENT,
    idRealizacao INT NOT NULL,
    idExercicio INT NOT NULL,
    respostaDada VARCHAR(10) NOT NULL,
    correta TINYINT(1) NOT NULL,

    PRIMARY KEY (idRespostaAtividade),
    UNIQUE KEY uq_resposta_realizacao_exercicio (idRealizacao, idExercicio),
    KEY idExercicio (idExercicio),

    CONSTRAINT fk_resposta_realizacao FOREIGN KEY (idRealizacao)
        REFERENCES RealizacaoAtividade(idRealizacao) ON DELETE CASCADE,
    CONSTRAINT fk_resposta_exercicio FOREIGN KEY (idExercicio)
        REFERENCES Exercicio(idExercicio)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;