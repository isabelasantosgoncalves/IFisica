# IFísica para Docentes

Plataforma web onde professores de física criam turmas, atividades e experimentos.

Aplicação Flask com MySQL, templates Jinja e uma API JSON consumida pelo próprio frontend.

## Estrutura

```
IFisica/
├── app.py                    fábrica da aplicação e registro dos blueprints
├── config.py                 leitura das variáveis de ambiente
├── database/
│   ├── db.py                 conexão única com o MySQL
│   └── schema.sql            criação do banco e das tabelas
├── routes/
│   ├── seguranca.py          proteção de rotas por sessão
│   ├── paginaRoutes.py       telas renderizadas
│   ├── authRoutes.py         cadastro, login e logout do docente
│   └── turmaRoutes.py        API de turmas
├── templates/                base.html e as telas que a estendem
└── static/
    ├── css/
    ├── js/
    └── images/
```

## Como rodar

Clone o projeto e crie o ambiente virtual:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Crie o banco de dados a partir do schema:

```bash
mysql -u root -p < database/schema.sql
```

Copie `.env.example` para `.env` e preencha com os dados do seu MySQL:

```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=sua_senha
DB_NAME=ifisica
SECRET_KEY=uma-chave-secreta-qualquer
```

Suba a aplicação:

```bash
python app.py
```

Acesse `http://localhost:5000`.

## Telas

| Rota | Tela |
| --- | --- |
| `/` | abertura, com criar conta e login |
| `/cadastro` | cadastro do docente |
| `/login` | entrada na plataforma |
| `/inicio` | página inicial com o menu e a lista de turmas |
| `/nova-turma` | passo 1, nome da turma |
| `/nova-turma/escolaridade` | passo 2, nível de escolaridade |
| `/nova-turma/origem` | passo 3, como conheceu a plataforma |

## API

Todas as rotas abaixo exigem sessão ativa e respondem em JSON.

| Método | Rota | Função |
| --- | --- | --- |
| `POST` | `/api/docentes` | cadastra um docente e já abre a sessão |
| `POST` | `/api/login` | autentica e abre a sessão |
| `GET` | `/logout` | encerra a sessão |
| `POST` | `/turmas` | cria uma turma para o docente logado |
| `GET` | `/turmas` | lista as turmas do docente logado |
| `GET` | `/turmas/<id>` | busca uma turma |
| `PUT` | `/turmas/<id>` | atualiza uma turma |
| `DELETE` | `/turmas/<id>` | exclui uma turma |
| `POST` | `/api/origem` | registra como o docente conheceu a plataforma |

## Modelo de dados

`Docente` guarda os dados pessoais e a senha com hash. `Turma` referencia `Docente` por
`idDocente`, com exclusão em cascata. O nível de escolaridade e o nome da turma são
coletados ao longo do fluxo de criação e gravados em um único INSERT no último passo.

## Próximos passos

- Atividades
- Experimentos
- Materiais de aula
- Relatórios
