-- Documentacao do banco IFisica, gerado a partir do servidor compartilhado.
-- Ja inclui as migracoes 001 a 007.
-- Banco COMPARTILHADO com o grupo do modulo de alunos.
-- Este arquivo NAO e a fonte da verdade: o servidor e. Ele existe para que
-- qualquer pessoa leia a estrutura sem precisar abrir o Workbench.
-- Somente aditivo: nunca acrescente DROP, TRUNCATE ou ALTER que remova coluna.


CREATE TABLE IF NOT EXISTS `Usuario` (
  `idUsuario` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `email` varchar(150) NOT NULL,
  `telefone` varchar(20) NOT NULL,
  `senha` varchar(255) NOT NULL,
  `dataNasc` date NOT NULL,
  `genero` varchar(60) DEFAULT NULL,
  `generoAutodeclarado` varchar(120) DEFAULT NULL,
  PRIMARY KEY (`idUsuario`),
  UNIQUE KEY `uq_usuario_email` (`email`),
  UNIQUE KEY `uq_usuario_telefone` (`telefone`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `Admin` (
  `idUsuario` int NOT NULL,
  PRIMARY KEY (`idUsuario`),
  CONSTRAINT `Admin_ibfk_1` FOREIGN KEY (`idUsuario`) REFERENCES `Usuario` (`idUsuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `Solicitacao` (
  `idSolicitacao` int NOT NULL AUTO_INCREMENT,
  `dataSolicitacao` date NOT NULL,
  `motivo` varchar(255) NOT NULL,
  `conteudo` varchar(255) DEFAULT NULL,
  `publicoAlvo` varchar(255) DEFAULT NULL,
  `status` int NOT NULL,
  `dataDecisao` date DEFAULT NULL,
  `idUsuario` int NOT NULL,
  `idAdmin` int DEFAULT NULL,
  PRIMARY KEY (`idSolicitacao`),
  KEY `idUsuario` (`idUsuario`),
  KEY `idAdmin` (`idAdmin`),
  CONSTRAINT `Solicitacao_ibfk_1` FOREIGN KEY (`idUsuario`) REFERENCES `Usuario` (`idUsuario`),
  CONSTRAINT `Solicitacao_ibfk_2` FOREIGN KEY (`idAdmin`) REFERENCES `Admin` (`idUsuario`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `Turma` (
  `idTurma` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `descricao` varchar(255) DEFAULT NULL,
  `dataCriacao` date NOT NULL,
  `nivel` int NOT NULL,
  `idUsuarioGerente` int NOT NULL,
  `idSolicitacao` int NOT NULL,
  `tipo` varchar(100) NOT NULL,
  `codigoConvite` varchar(8) DEFAULT NULL,
  PRIMARY KEY (`idTurma`),
  UNIQUE KEY `uq_turma_gerente_nome` (`idUsuarioGerente`,`nome`),
  UNIQUE KEY `uq_turma_codigo_convite` (`codigoConvite`),
  KEY `idx_turma_solicitacao` (`idSolicitacao`),
  CONSTRAINT `Turma_ibfk_1` FOREIGN KEY (`idUsuarioGerente`) REFERENCES `Usuario` (`idUsuario`),
  CONSTRAINT `Turma_ibfk_2` FOREIGN KEY (`idSolicitacao`) REFERENCES `Solicitacao` (`idSolicitacao`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `Participacao` (
  `idUsuario` int NOT NULL,
  `idTurma` int NOT NULL,
  PRIMARY KEY (`idUsuario`,`idTurma`),
  KEY `idTurma` (`idTurma`),
  CONSTRAINT `Participacao_ibfk_1` FOREIGN KEY (`idUsuario`) REFERENCES `Usuario` (`idUsuario`),
  CONSTRAINT `Participacao_ibfk_2` FOREIGN KEY (`idTurma`) REFERENCES `Turma` (`idTurma`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `SolicitacaoEntrada` (
  `idSolicitacaoEntrada` int NOT NULL AUTO_INCREMENT,
  `dataSolicitacao` date NOT NULL,
  `status` int NOT NULL,
  `idUsuario` int NOT NULL,
  `idTurma` int NOT NULL,
  PRIMARY KEY (`idSolicitacaoEntrada`),
  KEY `idUsuario` (`idUsuario`),
  KEY `idTurma` (`idTurma`),
  CONSTRAINT `SolicitacaoEntrada_ibfk_1` FOREIGN KEY (`idUsuario`) REFERENCES `Usuario` (`idUsuario`),
  CONSTRAINT `SolicitacaoEntrada_ibfk_2` FOREIGN KEY (`idTurma`) REFERENCES `Turma` (`idTurma`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `Exercicio` (
  `idExercicio` int NOT NULL AUTO_INCREMENT,
  `pergunta` varchar(500) NOT NULL,
  `alternativaA` varchar(255) DEFAULT NULL,
  `alternativaB` varchar(255) DEFAULT NULL,
  `alternativaC` varchar(255) DEFAULT NULL,
  `alternativaD` varchar(255) DEFAULT NULL,
  `alternativaCerta` varchar(255) DEFAULT NULL,
  `materia` varchar(100) NOT NULL,
  `dificuldade` varchar(50) NOT NULL,
  PRIMARY KEY (`idExercicio`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `Atividade` (
  `idAtividade` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(120) NOT NULL,
  `descricao` varchar(255) DEFAULT NULL,
  `idTurma` int NOT NULL,
  `dataCriacao` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`idAtividade`),
  KEY `idx_atividade_turma` (`idTurma`),
  CONSTRAINT `fk_atividade_turma` FOREIGN KEY (`idTurma`) REFERENCES `Turma` (`idTurma`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `AtividadeExercicio` (
  `idAtividade` int NOT NULL,
  `idExercicio` int NOT NULL,
  `ordem` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`idAtividade`,`idExercicio`),
  KEY `fk_atividade_exercicio_exercicio` (`idExercicio`),
  CONSTRAINT `fk_atividade_exercicio_atividade` FOREIGN KEY (`idAtividade`) REFERENCES `Atividade` (`idAtividade`) ON DELETE CASCADE,
  CONSTRAINT `fk_atividade_exercicio_exercicio` FOREIGN KEY (`idExercicio`) REFERENCES `Exercicio` (`idExercicio`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `RealizacaoAtividade` (
  `idRealizacao` int NOT NULL AUTO_INCREMENT,
  `idAtividade` int NOT NULL,
  `idUsuario` int NOT NULL,
  `dataRealizacao` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `pontuacao` int DEFAULT NULL,
  `totalQuestoes` int DEFAULT NULL,
  PRIMARY KEY (`idRealizacao`),
  UNIQUE KEY `uq_realizacao_atividade_usuario` (`idAtividade`,`idUsuario`),
  KEY `idUsuario` (`idUsuario`),
  CONSTRAINT `fk_realizacao_atividade` FOREIGN KEY (`idAtividade`) REFERENCES `Atividade` (`idAtividade`) ON DELETE CASCADE,
  CONSTRAINT `fk_realizacao_usuario` FOREIGN KEY (`idUsuario`) REFERENCES `Usuario` (`idUsuario`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `RespostaAtividade` (
  `idRespostaAtividade` int NOT NULL AUTO_INCREMENT,
  `idRealizacao` int NOT NULL,
  `idExercicio` int NOT NULL,
  `respostaDada` varchar(10) NOT NULL,
  `correta` tinyint(1) NOT NULL,
  PRIMARY KEY (`idRespostaAtividade`),
  UNIQUE KEY `uq_resposta_realizacao_exercicio` (`idRealizacao`,`idExercicio`),
  KEY `idExercicio` (`idExercicio`),
  CONSTRAINT `fk_resposta_exercicio` FOREIGN KEY (`idExercicio`) REFERENCES `Exercicio` (`idExercicio`),
  CONSTRAINT `fk_resposta_realizacao` FOREIGN KEY (`idRealizacao`) REFERENCES `RealizacaoAtividade` (`idRealizacao`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `Lista` (
  `idLista` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `descricao` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`idLista`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `ListaExercicio` (
  `idLista` int NOT NULL,
  `idExercicio` int NOT NULL,
  PRIMARY KEY (`idLista`,`idExercicio`),
  KEY `idExercicio` (`idExercicio`),
  CONSTRAINT `ListaExercicio_ibfk_1` FOREIGN KEY (`idLista`) REFERENCES `Lista` (`idLista`),
  CONSTRAINT `ListaExercicio_ibfk_2` FOREIGN KEY (`idExercicio`) REFERENCES `Exercicio` (`idExercicio`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `RealizarLista` (
  `idRealizacao` int NOT NULL AUTO_INCREMENT,
  `dataRealizacao` date NOT NULL,
  `idUsuario` int NOT NULL,
  `idLista` int NOT NULL,
  PRIMARY KEY (`idRealizacao`),
  KEY `idUsuario` (`idUsuario`),
  KEY `idLista` (`idLista`),
  CONSTRAINT `RealizarLista_ibfk_1` FOREIGN KEY (`idUsuario`) REFERENCES `Usuario` (`idUsuario`),
  CONSTRAINT `RealizarLista_ibfk_2` FOREIGN KEY (`idLista`) REFERENCES `Lista` (`idLista`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `Resposta` (
  `idResposta` int NOT NULL AUTO_INCREMENT,
  `idUsuario` int NOT NULL,
  `idExercicio` int NOT NULL,
  `respostaDada` varchar(255) NOT NULL,
  `idRealizacao` int NOT NULL,
  PRIMARY KEY (`idResposta`),
  KEY `idUsuario` (`idUsuario`),
  KEY `idExercicio` (`idExercicio`),
  KEY `idRealizacao` (`idRealizacao`),
  CONSTRAINT `Resposta_ibfk_1` FOREIGN KEY (`idUsuario`) REFERENCES `Usuario` (`idUsuario`),
  CONSTRAINT `Resposta_ibfk_2` FOREIGN KEY (`idExercicio`) REFERENCES `Exercicio` (`idExercicio`),
  CONSTRAINT `Resposta_ibfk_3` FOREIGN KEY (`idRealizacao`) REFERENCES `RealizarLista` (`idRealizacao`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `Ranking` (
  `idRanking` int NOT NULL AUTO_INCREMENT,
  `pontuacao` int DEFAULT NULL,
  `posicao` int DEFAULT NULL,
  `quantAcertos` int DEFAULT NULL,
  `idUsuario` int NOT NULL,
  `idTurma` int NOT NULL,
  PRIMARY KEY (`idRanking`),
  KEY `idUsuario` (`idUsuario`),
  KEY `idTurma` (`idTurma`),
  CONSTRAINT `Ranking_ibfk_1` FOREIGN KEY (`idUsuario`) REFERENCES `Usuario` (`idUsuario`),
  CONSTRAINT `Ranking_ibfk_2` FOREIGN KEY (`idTurma`) REFERENCES `Turma` (`idTurma`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
