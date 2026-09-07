-- Migracao 011 - arquivos guardados no banco
--
-- Rodar no Workbench com o script inteiro selecionado.
--
-- POR QUE:
-- ate agora a imagem da questao e o PDF do material eram gravados na pasta
-- static/uploads da maquina de quem enviou. Como cada pessoa roda a
-- aplicacao no proprio computador e so o BANCO e compartilhado, o arquivo
-- existia para quem enviou e para mais ninguem - a colega abria a questao e
-- via o espaco da imagem em branco.
--
-- Passando o conteudo para o banco, o arquivo acompanha o dado e aparece
-- para todo mundo.
--
-- MEDIUMBLOB guarda ate 16 MB por arquivo, e o max_allowed_packet do
-- servidor e 64 MB, entao os limites da aplicacao (3 MB de imagem e
-- 10 MB de PDF) cabem com folga.

USE IFisica;

CREATE TABLE IF NOT EXISTS Arquivo (
    idArquivo INT NOT NULL AUTO_INCREMENT,
    nome VARCHAR(160) NOT NULL,
    tipo VARCHAR(80) NOT NULL,
    tamanho INT NOT NULL,
    conteudo MEDIUMBLOB NOT NULL,
    idUsuario INT NOT NULL,
    dataEnvio DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (idArquivo),
    KEY idx_arquivo_usuario (idUsuario),

    CONSTRAINT fk_arquivo_usuario FOREIGN KEY (idUsuario)
        REFERENCES Usuario(idUsuario)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

ALTER TABLE Exercicio
    ADD COLUMN idImagem INT NULL AFTER imagem,
    ADD CONSTRAINT fk_exercicio_imagem FOREIGN KEY (idImagem)
        REFERENCES Arquivo(idArquivo) ON DELETE SET NULL;

ALTER TABLE Material
    ADD COLUMN idArquivo INT NULL AFTER arquivo,
    ADD CONSTRAINT fk_material_arquivo FOREIGN KEY (idArquivo)
        REFERENCES Arquivo(idArquivo) ON DELETE SET NULL;

-- As colunas antigas Exercicio.imagem e Material.arquivo guardavam o nome do
-- arquivo em disco. Ficam no banco por seguranca, mas a aplicacao nao escreve
-- mais nelas. As imagens enviadas antes desta migracao precisam ser enviadas
-- de novo pela tela, porque o arquivo so existe na maquina de quem enviou.

-- Conferencia: a tabela Arquivo e as duas colunas novas.
SELECT 'tabela Arquivo' AS item, COUNT(*) AS achou
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'IFisica' AND TABLE_NAME = 'Arquivo'
UNION ALL
SELECT 'Exercicio.idImagem', COUNT(*)
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'IFisica' AND TABLE_NAME = 'Exercicio' AND COLUMN_NAME = 'idImagem'
UNION ALL
SELECT 'Material.idArquivo', COUNT(*)
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'IFisica' AND TABLE_NAME = 'Material' AND COLUMN_NAME = 'idArquivo';
