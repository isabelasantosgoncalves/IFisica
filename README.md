# IFísica para Docentes

Plataforma web onde professores de física criam turmas, atividades e experimentos.

Aplicação Flask com MySQL, templates Jinja e uma API JSON consumida pelo próprio frontend.

## Estrutura

```
IFisica/
├── app.py                    fábrica da aplicação e registro dos blueprints
├── config.py                 leitura das variáveis de ambiente
├── database/
│   ├── db.py                 pool de conexões e cursor com commit/rollback
│   ├── schema.sql            retrato do banco compartilhado
│   └── migracoes/            alterações a rodar no Workbench, em ordem
├── models/
│   ├── constantes.py         níveis, gêneros, status e papéis
│   ├── usuario.py            usuário e papel (estudante/tutor/admin)
│   ├── solicitacao.py        pedido de permissão de tutor
│   ├── turma.py              sala, código de convite e participantes
│   ├── exercicio.py          banco de questões
│   ├── atividade.py          atividade e suas questões
│   ├── resposta_atividade.py respostas do estudante e pontuação
│   ├── material.py           materiais de estudo
│   ├── desempenho.py         ranking, relatório e faixas de nível
│   └── perfil.py             edição dos dados e da senha
├── routes/
│   ├── seguranca.py          sessão e permissão por papel
│   ├── utilitarios.py        normalização de entrada e datas
│   ├── paginaRoutes.py       telas renderizadas
│   ├── authRoutes.py         cadastro e login
│   ├── solicitacaoRoutes.py  tutoria e painel do administrador
│   ├── turmaRoutes.py        salas
│   ├── salaRoutes.py         entrada do estudante numa sala
│   ├── exercicioRoutes.py    banco de questões
│   ├── atividadeRoutes.py    atividades da sala
│   ├── respostaRoutes.py     estudante respondendo atividade
│   ├── materialRoutes.py     materiais de estudo da sala
│   ├── desempenhoRoutes.py   ranking, relatório e nível
│   ├── perfilRoutes.py       perfil e troca de senha
│   └── uploadRoutes.py       envio de imagem e PDF
├── templates/                base.html e as telas que a estendem
└── static/
    ├── css/
    ├── js/
    ├── docs/                 guia prático em PDF
    └── images/
```

## Como rodar na sua máquina (Windows)

O repositório fica em `Documentos\GitHub\IFisica`. Todos os comandos abaixo são rodados
de dentro dessa pasta, no PowerShell.

### 1. Ambiente virtual e dependências

Já estão criados. Se um dia precisar refazer:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Se o PowerShell reclamar de política de execução ao ativar, use `.\venv\Scripts\python.exe`
direto nos comandos, sem ativar o ambiente.

### 2. Arquivo de credenciais

**Obrigatório. Sem ele a aplicação nem sobe — `criar_app()` avisa qual variável falta.**

O banco fica num **servidor compartilhado** com o grupo do módulo de alunos, não no MySQL da sua
máquina. O `.env` não vai para o repositório. Copie o `.env.example` para `.env` e preencha com os
dados do servidor:

```
DB_HOST=endereco_do_servidor
DB_PORT=3306
DB_USER=usuario_do_servidor
DB_PASSWORD=senha_desse_usuario
DB_NAME=ifisica
SECRET_KEY=uma-sequencia-aleatoria-longa
```

Deixar `DB_HOST=localhost` e `DB_USER=root` faz o Python bater no MySQL da sua própria máquina e
falhar com `Access denied for user 'root'@'localhost'`. Os valores certos estão no MySQL Workbench:
botão direito na conexão do IFísica → `Edit Connection` → **Hostname**, **Port** e **Username**.

`SECRET_KEY` assina o cookie de sessão do login. Não pode ser frase com sentido — se for
adivinhável, dá para forjar um cookie e entrar como qualquer docente. Gere com:

```powershell
.\venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
```

### 3. O banco

As tabelas já existem no servidor compartilhado — `database/schema.sql` é o retrato delas,
somente aditivo, sem `DROP` nem `TRUNCATE`.

As migrações de `database/migracoes/` **já foram aplicadas no servidor**. Ficam no repositório
para o histórico e para quem precisar montar o banco do zero — nesse caso, no Workbench,
`File` → `Open SQL Script`, uma de cada vez, na ordem:

| Arquivo | O que faz | Obrigatória |
| --- | --- | --- |
| `001_auto_increment.sql` | põe `AUTO_INCREMENT` em 8 chaves primárias | sim, nada insere sem ela |
| `002_email_unico.sql` | separa o índice `UNIQUE (email, telefone)` em dois | recomendada |
| `003_papeis_e_solicitacao.sql` | gênero, conteúdo/público-alvo da solicitação, e solta o `UNIQUE` de `Turma.idSolicitacao` | sim |
| `004_nome_turma_por_tutor.sql` | nome de sala passa a ser único por tutor, não global | sim |
| `005_codigo_convite.sql` | `tipo` com padrão e `codigoConvite` na sala | sim |
| `006_renomear_titulo_atividade.sql` | `Atividade.titulo` vira `Atividade.nome` | sim |
| `007_resposta_atividade.sql` | tabelas `RealizacaoAtividade` e `RespostaAtividade` | sim |
| `008_resolucao_exercicio.sql` | `resolucao` na questão, mostrada ao aluno na correção | sim |
| `009_imagem_exercicio.sql` | `imagem` na questão | sim |
| `010_materiais.sql` | tabela `Material` (links e PDFs por assunto) | sim |
| `011_arquivos_no_banco.sql` | tabela `Arquivo`: imagens e PDFs passam a viver no banco | sim |

Como o banco é compartilhado com o grupo do módulo de alunos, qualquer migração nova precisa
ser combinada antes de rodar. `conferencia.sql` confere as quatro primeiras.

### 4. Subir a aplicação

```powershell
.\venv\Scripts\python.exe app.py
```

Acesse `http://localhost:5000`.

### 5. Administrador

Já existe um administrador no banco: **admin@gmail.com**. É a conta que aprova os pedidos de
permissão de tutor.

Para promover outra pessoa, a tabela `Admin` recebe o id dela — não há caminho pela aplicação:

```sql
SELECT idUsuario, nome, email FROM IFisica.Usuario;
INSERT INTO IFisica.Admin (idUsuario) VALUES (O_ID);
```

## Papéis

Não existe coluna de papel em `Usuario` — ele é **derivado**, em `models/usuario.py`:

- **administrador** — tem linha em `Admin`
- **tutor** — tem uma `Solicitacao` com `status = 1` (aprovada)
- **estudante** — todo o resto, que é como todo cadastro começa

Como o papel é lido a cada requisição, aprovar uma solicitação libera as funcionalidades de
tutor na hora, sem sincronizar coluna nenhuma.

**Permissão de ensinar é coisa separada do rótulo do papel.** Quem cria turma é quem tem uma
solicitação aprovada (`usuario.e_tutor`), não quem tem um rótulo. Um administrador não vira
tutor de graça: se quiser dar aula, pede permissão como qualquer pessoa. É por isso que
`routes/seguranca.py` tem `pode_ensinar()` ao lado de `papel_atual()`.

Decorators disponíveis:

| Decorator | Protege | Quem não passa |
| --- | --- | --- |
| `login_obrigatorio` | páginas | vai para `/login` |
| `login_obrigatorio_api` | rotas JSON | recebe `401` |
| `ensino_obrigatorio` | páginas de turma | vai para `/solicitar-tutor` |
| `tutor_obrigatorio_api` | rotas de turma | recebe `403` |
| `admin_obrigatorio_api` | rotas do painel | recebe `403` |
| `papel_obrigatorio(...)` | páginas por papel | volta para `/inicio` |

Nenhuma tela leva a um beco sem saída: o estudante que clica em "Turma" cai no formulário de
solicitação em vez de num erro.

## Telas

| Rota | Tela |
| --- | --- |
| `/` | abertura, com criar conta e login |
| `/cadastro` | cadastro do usuário |
| `/login` | entrada na plataforma |
| `/inicio` | página inicial: salas em que participa, entrar em sala, suas salas |
| `/nova-turma` | passo 1, nome e descrição da sala (tutor) |
| `/nova-turma/escolaridade` | passo 2, nível de escolaridade, e criação (tutor) |
| `/turma/<id>` | a sala: alunos, pedidos, questões e atividades |
| `/turma/<id>/atividades/<id>` | estudante respondendo a atividade |
| `/solicitar-tutor` | formulário de pedido de permissão de tutor |
| `/admin/solicitacoes` | painel do administrador |
| `/turma/<id>/relatorio` | relatório de desempenho da sala (responsável) |
| `/perfil` | dados pessoais, nível e salas do usuário |
| `/configuracoes` | troca de senha e sessão |
| `/sobre` | o que é o IFísica |
| `/ajuda` | guia prático de uso, por tela |

A página da sala é a mesma para tutor e estudante: o front esconde código de convite, pedidos
de entrada, banco de questões e criação de atividades para quem não é o responsável.

## API

Todas as rotas de dados vivem sob `/api` e respondem JSON. Exceto o cadastro e o login,
todas exigem sessão ativa.

| Método | Rota | Função |
| --- | --- | --- |
| `POST` | `/api/usuarios` | cadastra um usuário e já abre a sessão |
| `POST` | `/api/login` | autentica e abre a sessão |
| `POST` | `/api/solicitacoes` | envia um pedido de permissão de tutor |
| `GET` | `/api/solicitacoes/minha` | situação do próprio pedido |
| `GET` | `/api/solicitacoes` | lista os pendentes (administrador) |
| `GET` | `/api/solicitacoes/<id>` | detalha um pedido (administrador) |
| `PUT` | `/api/solicitacoes/<id>` | aprova ou recusa (administrador) |
| `POST` | `/api/turmas` | cria uma sala (exige tutoria aprovada) |
| `GET` | `/api/turmas` | lista as salas que o usuário gerencia |
| `GET` | `/api/turmas/minhas-participacoes` | lista as salas em que o usuário entrou |
| `GET` | `/api/turmas/<id>` | dados da sala, com `souGerente` |
| `PUT` `/` `DELETE` | `/api/turmas/<id>` | atualiza ou exclui a sala |
| `GET` | `/api/turmas/<id>/participantes` | alunos da sala (responsável) |
| `POST` | `/api/salas/entrar` | estudante pede entrada com o código de convite |
| `GET` | `/api/turmas/<id>/solicitacoes-entrada` | pedidos pendentes (responsável) |
| `PUT` | `/api/solicitacoes-entrada/<id>` | aprova ou recusa a entrada (responsável) |
| `GET` `/` `POST` | `/api/exercicios` | banco de questões (só tutor) |
| `POST` | `/api/uploads/exercicios` | envia a imagem de uma questão (só tutor) |
| `POST` | `/api/uploads/materiais` | envia um PDF de material (só tutor) |
| `GET` | `/api/turmas/<id>/materiais` | materiais da sala, agrupados por assunto |
| `POST` `/` `PUT` `/` `DELETE` | `/api/turmas/<id>/materiais[/<id>]` | gerencia materiais (responsável) |
| `GET` | `/api/turmas/<id>/ranking` | ranking da sala por acertos |
| `GET` | `/api/meu-progresso` | questões respondidas, acertos e nível do usuário |
| `GET` | `/api/turmas/<id>/relatorio` | desempenho por aluno, atividade e questão (responsável) |
| `GET` | `/api/perfil` | dados do usuário, nível e salas |
| `PUT` | `/api/perfil` | edita nome, telefone e gênero |
| `PUT` | `/api/perfil/senha` | troca a senha, conferindo a atual |
| `PUT` `/` `DELETE` | `/api/exercicios/<id>` | edita ou remove uma questão |
| `GET` `/` `POST` | `/api/turmas/<id>/atividades` | atividades da sala |
| `GET` `/` `PUT` `/` `DELETE` | `/api/turmas/<id>/atividades/<id>` | uma atividade |
| `GET` | `/api/turmas/<id>/atividades/<id>/questoes` | questões para responder, sem gabarito |
| `POST` | `/api/turmas/<id>/atividades/<id>/respostas` | envia as respostas e recebe a pontuação |

`GET /logout` não é API: encerra a sessão e redireciona para a abertura.

### Contrato para quem for consumir

- **Autenticação**: cookie de sessão do Flask, assinado com `SECRET_KEY`. Sem sessão, as rotas
  de dados devolvem `401` com `{"erro": "Sessão expirada. Faça login novamente."}`.
- **Erro**: sempre `{"erro": "mensagem"}`, com `detalhes` só quando o erro veio do MySQL.
- **Turma**: `idTurma`, `nome`, `descricao`, `dataCriacao`, `nivel`, `idUsuarioGerente`,
  `idSolicitacao`, `tipo`, mais `nivelRotulo` calculado. As colunas são listadas explicitamente
  nas consultas — colunas novas criadas por outro grupo não vazam para a resposta nem quebram
  o frontend.
- **Datas**: sempre `dd/mm/aaaa` nas respostas, não o formato cru do HTTP.
- **Escopo**: toda rota de turma filtra por `idDocente` da sessão. Um docente nunca lê nem altera
  turma de outro.

## Modelo de dados

O banco é compartilhado e tem 12 tabelas. As que esta parte usa:

- **`Usuario`** — toda pessoa da plataforma. Não distingue papel; isso é derivado.
- **`Admin`** — herda de `Usuario` pela chave primária. Quem está aqui é administrador.
- **`Solicitacao`** — pedido de permissão de tutor, com motivo, conteúdo, público-alvo e status.
- **`Turma`** — pertence a um tutor por `idUsuarioGerente` e aponta para a `Solicitacao`
  que autorizou aquele tutor.

As demais (`Exercicio`, `Lista`, `ListaExercicio`, `RealizarLista`, `Resposta`, `Ranking`,
`Participacao`, `SolicitacaoEntrada`) são do módulo de alunos e de exercícios.

## Estado atual

Funciona de ponta a ponta: cadastro com gênero autodeclarado, login, pedido e aprovação de
tutoria, criação de sala com código de convite, banco de questões, montagem de atividades,
entrada do estudante na sala mediante aprovação do responsável, e o estudante respondendo a
atividade e recebendo a pontuação na hora.

O gabarito nunca é enviado ao estudante: a correção acontece no servidor, e a rota do banco
de questões é restrita a tutores. Depois de responder, o estudante vê a correção questão por
questão — o que marcou, qual era a certa e a resolução escrita pelo professor.

Questões aceitam imagem opcional (JPG, PNG, GIF ou WEBP, até 3 MB) e materiais aceitam PDF
(até 10 MB). O arquivo é validado pelo conteúdo, não pela extensão, e **fica guardado no
banco**, na tabela `Arquivo`, servido por `/api/arquivos/<id>`.

Guardar em disco não funcionaria aqui: cada pessoa roda a aplicação no próprio computador e só
o banco é compartilhado, então um arquivo salvo em disco existiria apenas para quem o enviou.

Pendências ficam visíveis: a página inicial do administrador avisa quantos pedidos de tutoria
aguardam análise, e cada sala do tutor mostra quantos pedidos de entrada tem.

A sala tem quatro abas: alunos, atividades, materiais e ranking. Materiais são links ou PDFs
agrupados por assunto, que o responsável adiciona, edita e remove.

## Gamificação

O **ranking da sala** é calculado na hora, a partir das atividades respondidas: soma dos acertos,
com empate desfeito por quem respondeu menos questões. Não há tabela de ranking a sincronizar.

O **nível do estudante** é geral, não por sala, e vem da quantidade de questões respondidas.
As faixas estão em `NIVEIS_ALUNO`, em `models/constantes.py`:

| Questões respondidas | Nível |
| --- | --- |
| 0 | Iniciante |
| 10 | Aprendiz |
| 25 | Praticante |
| 50 | Avançado |
| 100 | Mestre |
| 200 | Lenda da Física |

Mudar as faixas é editar essa tupla; nada no banco precisa mudar.

## Relatório do tutor

Em cada sala, o responsável tem um relatório com:

- **Resumo**: alunos na sala, quantos já responderam, quantos ainda não, número de atividades
  e aproveitamento geral
- **Questões que mais derrubaram**: as cinco com menor percentual de acerto, com barra visual
- **Por aluno**: atividades feitas, acertos e aproveitamento
- **Por atividade**: quem fez, acertos e média
- **Por questão**: respostas, acertos e percentual

Tudo calculado na hora a partir das respostas, sem tabela intermediária.

## Integração com o módulo de alunos

O outro grupo desenvolveu em **Java / Spring Boot**, com um modelo de dados próprio
(`Aluno` e `Professor` separados, nomes em `snake_case`, tabela `Niveis`). Esse modelo é
incompatível com o daqui e o script deles **não deve ser aplicado ao banco**: ele cria `Turma`
e `Atividade`, que já existem com outra estrutura.

O material deles ficou arquivado fora do projeto, apenas como registro. Esta aplicação já cobre
o que aquele backend fazia, e ainda tem papéis, aprovação de tutoria, código de convite e
correção automática.

O banco continua compartilhado, então valem os cuidados:

- `database/schema.sql` é **somente aditivo** — sem `DROP` nem `TRUNCATE`
- Nenhuma consulta usa `SELECT *`, então colunas novas não alteram as respostas desta API
- Todas as rotas de dados estão sob `/api`
- A leitura da sessão está isolada em `routes/seguranca.py`

## Próximos passos

- Materiais e atividades ainda são por sala; um acervo compartilhado entre as salas do mesmo
  tutor evitaria recadastrar a mesma questão
- Exportar o relatório da sala em PDF
- Notificar o estudante quando a entrada na sala for aprovada

## Scripts de apoio

Em `database/migracoes/`, todos para abrir no Workbench:

- `conferencia.sql` — confere as quatro migrações de uma vez. Só leitura.
- `limpeza_dados_teste.sql` — apaga as contas de teste (`@exemplo.com`) e o que pendura nelas.

## Pendências de modelagem

- `Turma.nivel` (código 1 a 5) e `Turma.tipo` (o mesmo em texto) guardam a escolaridade da sala.
  São redundantes, mas o código mantém as duas em sincronia sozinho: `rotulo_do_nivel`, em
  `models/turma.py`, deriva o texto do código ao criar e ao editar. Decisão da equipe: deixar
  como está.
- Os valores de `Solicitacao.status` foram assumidos como `0` pendente, `1` aprovada,
  `2` recusada.
- `Turma.idSolicitacao` é `NOT NULL`, então só quem é tutor aprovado consegue criar sala.
- O banco é acessado como `root` num servidor aberto à internet. Decisão da equipe: manter,
  já que o projeto não vai ao ar e é trabalho de escola.
