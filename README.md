# VetCare — Sistema de Gestão para Clínica Veterinária

Trabalho II de Engenharia de Software 1 (UFBA) — Sprint 1 de implementação.
Backend em **Python (Flask) + SQLite** e frontend em **HTML + JavaScript puro**.

## Requisitos implementados nesta Sprint (5 de 17 ≈ 29%)

| Requisito | Descrição | Prioridade |
|---|---|---|
| REQ01 | Manter Usuário (perfis: Administrador, Recepcionista, Veterinário) | Alta |
| REQ02 | Autenticar Usuário (login com token JWT) | Alta |
| REQ04 | Manter Tutor | Alta |
| REQ05 | Manter Animal (sempre associado a um tutor) | Alta |
| REQ06 | Manter Veterinário | Alta |

Também está implementado o atributo de qualidade **Segurança**: controle de acesso por perfil (RBAC).

| Perfil | Usuários | Tutores e Animais | Veterinários |
|---|---|---|---|
| Administrador | ler e alterar | ler e alterar | ler e alterar |
| Recepcionista | sem acesso | ler e alterar | só ler |
| Veterinário | sem acesso | só ler | só ler |

## Como rodar

Pré-requisito: Python 3.10 ou superior.

```bash
git clone <URL-DO-REPOSITORIO>
cd vetcare
python -m venv .venv
source .venv/bin/activate       
pip install -r requirements.txt
python app.py
```

Abra **http://127.0.0.1:5000** no navegador.

Usuário inicial (criado automaticamente na primeira execução):

- e-mail: `admin@vetcare.com`
- senha: `admin123`

Use esse usuário para criar os demais (Recepcionista e Veterinário) na aba **Usuários**.
O banco é o arquivo `vetcare.db`, criado na primeira execução; para zerar os dados, apague o arquivo.

Variáveis de ambiente opcionais: `VETCARE_SECRET` (chave de assinatura do token — defina uma própria fora do
ambiente de desenvolvimento) e `VETCARE_ADMIN_SENHA` (senha do administrador inicial).

## Testes

```bash
python -m unittest discover -s tests -v
```

## Estrutura (monólito modular em camadas — ADR-001)

```
app.py                  ponto de entrada; registra os módulos
transversal/            db.py (SQLite), seguranca.py (JWT + RBAC), crud.py (base), erros.py
modulos/
  auth/                 login (REQ02)
  usuarios/             REQ01
  tutores/              REQ04
  animais/              REQ05
  veterinarios/         REQ06
    rotas.py            camada de apresentação (HTTP)
    servico.py          regras de negócio e validações
    repositorio.py      acesso ao banco
frontend/               login.html, index.html, app.js, style.css
tests/                  testes automatizados da API
docs/ADRs-Etapa2.md     ADRs 007 a 009 (desvios em relação à Etapa 1)
```

## API (resumo)

Todas as rotas, exceto `POST /api/login`, exigem o cabeçalho `Authorization: Bearer <token>`.

| Método e rota | Função |
|---|---|
| `POST /api/login` | corpo `{email, senha}`; devolve `{token, usuario}` |
| `GET /api/me` | usuário autenticado |
| `GET, POST /api/{usuarios,tutores,animais,veterinarios}` | listar e criar |
| `GET, PUT, DELETE /api/{recurso}/<id>` | consultar, alterar e excluir |

Erros voltam como JSON `{"erro": "mensagem"}` com os códigos 400 (dados inválidos), 401 (não autenticado),
403 (sem permissão), 404 e 409 (duplicado ou vínculo existente, ex.: tutor com animais).

## Decisões arquiteturais

ADRs da Etapa 1: ADR-001 a ADR-006 (documento de arquitetura). ADRs desta etapa: [docs/ADRs-Etapa2.md](docs/ADRs-Etapa2.md)
(SQLite no lugar de PostgreSQL, escolha da stack e Flask como ponto único de entrada).
