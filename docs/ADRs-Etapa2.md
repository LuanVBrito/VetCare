# VetCare — ADRs da Etapa 2 (Implementação)

Estes ADRs registram os **desvios e as decisões novas** em relação à arquitetura da Etapa 1
(`VetCare_Arquitetura_Documento`, ADR-001 a ADR-006). Os ADRs 001 a 006 continuam válidos, com as
ressalvas indicadas abaixo.

| ADR | Título | Relação com a Etapa 1 |
|---|---|---|
| ADR-007 | SQLite no lugar de PostgreSQL nesta Sprint | Desvia do ADR-006 |
| ADR-008 | Stack: Python (Flask) no backend e JavaScript puro no frontend | Decisão nova (a Etapa 1 não definia stack) |
| ADR-009 | Flask como ponto único de entrada, sem API Gateway/BFF separado | Desvia da Seção 4.1 (API Gateway/BFF) e ajusta o ADR-002 |

Itens da Etapa 1 **adiados** (não são desvio, apenas ficam fora do escopo da Sprint por dependerem de requisitos
ainda não implementados): ADR-003 (redundância de instâncias e balanceador) e ADR-004 (fila de mensagens para
notificações, ligada ao REQ16). Serão retomados na etapa final.

---

## ADR-007: SQLite como banco de dados nesta Sprint

**Status:** Aceito (substitui parcialmente o ADR-006)

**Contexto**

O ADR-006 definiu PostgreSQL pela integridade referencial e pelas transações ACID. Nesta Sprint, o sistema roda em
uma única máquina, com poucos usuários, e o projeto precisa ser executado facilmente por quem avalia (clonar o
repositório e rodar). Instalar e configurar um servidor PostgreSQL adiciona uma barreira sem benefício nesse volume.

**Decisão**

Usar SQLite (módulo `sqlite3` da biblioteca padrão do Python). As garantias que motivaram o ADR-006 foram
mantidas: transações em cada escrita, `PRAGMA foreign_keys = ON`, chaves estrangeiras com `ON DELETE RESTRICT`
(um tutor com animais não pode ser excluído) e restrições `UNIQUE` e `CHECK`. Todo o acesso ao banco fica na camada
de repositórios e em `transversal/db.py`, sem SQL espalhado nas rotas.

**Consequências**

• Positiva: nenhuma instalação além de `pip install`; o banco é o arquivo `vetcare.db`.
• Positiva: integridade referencial e transações continuam garantidas, como previsto na Etapa 1.
• Negativa: limitação de escrita concorrente e de escalabilidade, conhecida desde o ADR-006.
• Mitigação: como o SQL está isolado nos repositórios, a migração para PostgreSQL na etapa final exige trocar a
  conexão em `transversal/db.py` e ajustar poucas diferenças de sintaxe (tipos e `AUTOINCREMENT`).

---

## ADR-008: Python (Flask) no backend e JavaScript puro no frontend

**Status:** Aceito

**Contexto**

A Etapa 1 definiu o estilo (monólito modular em camadas) mas não a tecnologia. A equipe precisa de uma stack que a
própria equipe domine, com o mínimo de configuração e que permita manter a separação em módulos e camadas.

**Decisão**

Backend em Python com Flask, organizado em `modulos/<nome>/` com `repositorio.py` (infraestrutura), `servico.py`
(regras de negócio) e `rotas.py` (apresentação), mais um pacote `transversal/` (banco, segurança, erros, base de
CRUD), espelhando as camadas e o pacote transversal do ADR-001. Frontend em HTML e JavaScript puro (`fetch`), sem
framework e sem etapa de build, servido pelo próprio Flask.

**Consequências**

• Positiva: poucas dependências (`Flask` e `PyJWT`); o sistema sobe com `python app.py`.
• Positiva: cada módulo pode evoluir sem alterar os demais; novos módulos só registram um blueprint.
• Negativa: JavaScript puro não oferece componentes prontos; telas mais complexas (agenda, prontuário) darão mais
  trabalho do que em um framework. Se necessário, a decisão será revista na etapa final.

---

## ADR-009: Flask como ponto único de entrada (sem API Gateway/BFF separado)

**Status:** Aceito (ajusta o ADR-002)

**Contexto**

A Etapa 1 previa um componente API Gateway/BFF na camada de apresentação, responsável por roteamento e
autenticação de sessão, e o ADR-002 previa a verificação de permissões (RBAC) nesse gateway e em cada módulo. Em um
monólito de uma única implantação, um gateway separado seria um componente a mais sem função distinta.

**Decisão**

A própria aplicação Flask recebe todas as requisições e faz o papel do gateway. A autenticação continua centralizada
(`modulos/auth` emite o token JWT; `transversal/seguranca.py` o valida) e o RBAC é aplicado por um decorador
(`exigir_perfil`) em cada rota. O decorador confere o usuário e o perfil no banco a cada requisição, e não apenas
no token, de modo que a exclusão de um usuário ou a mudança de perfil valem imediatamente.

**Consequências**

• Positiva: menos um componente para implantar e manter; a regra de permissão fica visível ao lado de cada rota.
• Positiva: o ponto único de verdade para identidade e permissões do ADR-002 é preservado.
• Negativa: uma consulta ao banco a mais por requisição autenticada (aceitável no volume atual).
• Negativa: se o sistema evoluir para vários serviços, será preciso extrair um gateway real.
