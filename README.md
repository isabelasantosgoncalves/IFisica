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
│   ├── usuario.py            SQL do usuário e papel (estudante/tutor/admin)
│   ├── solicitacao.py        SQL do pedido de permissão de tutor
│   └── turma.py              SQL da turma
├── routes/
│   ├── seguranca.py          sessão e permissão por papel
│   ├── utilitarios.py        normalização de entrada
│   ├── paginaRoutes.py       telas renderizadas
│   ├── authRoutes.py         cadastro e login do usuário
│   ├── solicitacaoRoutes.py  pedido de tutoria e decisão do administrador
│   └── turmaRoutes.py        API de turmas
├── templates/                base.html e as telas que a estendem
└── static/
    ├── css/
    ├── js/
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

Faltam as migrações de `database/migracoes/`, que **precisam ser combinadas com a colega**
antes de rodar, porque o banco é dos dois grupos. No Workbench, `File` → `Open SQL Script`,
uma de cada vez, na ordem:

| Arquivo | O que faz | Obrigatória |
| --- | --- | --- |
| `001_auto_increment.sql` | põe `AUTO_INCREMENT` em 8 chaves primárias | sim, nada insere sem ela |
| `002_email_unico.sql` | separa o índice `UNIQUE (email, telefone)` em dois | recomendada |
| `003_papeis_e_solicitacao.sql` | gênero, conteúdo/público-alvo da solicitação, e solta o `UNIQUE` de `Turma.idSolicitacao` | sim, para o cadastro e as turmas |
| `004_nome_turma_por_tutor.sql` | nome de turma passa a ser único por tutor, não global | sim |

### 4. Subir a aplicação

```powershell
.\venv\Scripts\python.exe app.py
```

Acesse `http://localhost:5000`.

### 5. Criar o primeiro administrador

A tabela `Admin` nasce vazia, e sem ninguém nela não existe quem aprove solicitações de tutor.
Depois de se cadastrar pela tela, descubra seu id e insira:

```sql
SELECT idUsuario, nome, email FROM IFisica.Usuario;
INSERT INTO IFisica.Admin (idUsuario) VALUES (SEU_ID);
```

Recarregue `/inicio`: o menu passa a mostrar "Solicitações pendentes".

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
| `/cadastro` | cadastro do docente |
| `/login` | entrada na plataforma |
| `/inicio` | página inicial com o menu e a lista de turmas |
| `/nova-turma` | passo 1, nome e descrição da turma (tutor) |
| `/nova-turma/escolaridade` | passo 2, nível de escolaridade, e criação (tutor) |
| `/solicitar-tutor` | formulário de pedido de permissão de tutor |
| `/admin/solicitacoes` | painel do administrador com os pedidos pendentes |

## API

Todas as rotas de dados vivem sob `/api` e respondem JSON. Exceto o cadastro e o login,
todas exigem sessão ativa.

| Método | Rota | Função |
| --- | --- | --- |
| `POST` | `/api/usuarios` | cadastra um usuário e já abre a sessão |
| `POST` | `/api/login` | autentica e abre a sessão |
| `POST` | `/api/turmas` | cria uma turma (exige papel de tutor) |
| `GET` | `/api/turmas` | lista as turmas que o usuário gerencia |
| `GET` | `/api/turmas/<id>` | busca uma turma |
| `PUT` | `/api/turmas/<id>` | atualiza uma turma |
| `DELETE` | `/api/turmas/<id>` | exclui uma turma |
| `POST` | `/api/solicitacoes` | envia um pedido de permissão de tutor |
| `GET` | `/api/solicitacoes/minha` | situação do próprio pedido |
| `GET` | `/api/solicitacoes` | lista os pendentes (administrador) |
| `GET` | `/api/solicitacoes/<id>` | detalha um pedido (administrador) |
| `PUT` | `/api/solicitacoes/<id>` | aprova ou recusa, com `{"aprovar": true}` ou `false` (administrador) |

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

Pronto: cadastro com gênero autodeclarado, login, sessão, papéis derivados, proteção de rotas
por papel, CRUD de turmas e as seis telas. O SQL fica em `models/`, as rotas só validam entrada
e formatam resposta, e as conexões saem de um pool com `commit`/`rollback` garantidos.

## Integração com o módulo de alunos

O módulo de alunos é de outro grupo e será acoplado depois. O que já está preparado:

- O banco é compartilhado, então `database/schema.sql` é **somente aditivo** — sem `DROP` nem
  `TRUNCATE`. A fonte da verdade é o servidor; o arquivo documenta.
- Nenhuma consulta usa `SELECT *`. Colunas novas nas tabelas compartilhadas não alteram as
  respostas desta API.
- Todas as rotas de dados estão sob `/api`, então `/api/alunos` encaixa sem conflito.
- O elo entre os dois módulos é `Turma.idTurma`. É essa a chave que a matrícula do aluno deve
  referenciar — não criar outra.
- A leitura da sessão está isolada em `routes/seguranca.py`. Se o módulo de alunos for uma
  aplicação separada, o cookie não atravessa e vai ser preciso um contrato de token; trocar o
  mecanismo mexe só nesse arquivo.

## Próximos passos

A seção 1 do documento de funcionalidades, **Contas e Permissões**, está completa: cadastro com
gênero autodeclarado, login, solicitação de permissão de tutor, painel do administrador e
aprovação/recusa que libera as funcionalidades de tutor.

Ainda por fazer, já com tabelas prontas no banco:

- Exercícios, listas e realização de listas
- Ranking e participação em turma
- `SolicitacaoEntrada`: aluno pedindo para entrar numa turma
- Materiais de aula e relatórios

## Scripts de apoio

Em `database/migracoes/`, todos para abrir no Workbench:

- `conferencia.sql` — confere as quatro migrações de uma vez. Só leitura.
- `limpeza_dados_teste.sql` — apaga as contas de teste (`@exemplo.com`) e o que pendura nelas.

## Pendências de modelagem

Pontos a resolver com o grupo do banco:

- `Turma.tipo` é `VARCHAR(100) NOT NULL` e ninguém documentou o que representa. O código
  grava `"Regular"` (`TIPO_PADRAO` em `models/constantes.py`) até haver definição.
- Os valores de `Solicitacao.status` foram assumidos como `0` pendente, `1` aprovada,
  `2` recusada. Confirmar.
- `Turma.idSolicitacao` é `NOT NULL`, então só quem é tutor aprovado consegue criar turma.
  É coerente com o fluxo, mas amarra as duas coisas de forma rígida.
