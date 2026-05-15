# Contexto para o Codex — Atualização do Sistema de Campanha Django

## Objetivo deste arquivo

Este arquivo deve ser usado como contexto antes de alterar o projeto.

O projeto **já existe** e já possui um CRUD simples de pessoas e um relatório básico. A tarefa não é reconstruir o sistema do zero, nem trocar a stack. A tarefa é evoluir o sistema atual de forma incremental, simples e organizada.

Prioridade máxima:

- preservar a estrutura atual;
- evitar overengineering;
- fazer pequenas mudanças úteis;
- manter o código fácil de entender e manter;
- não adicionar frontend framework;
- não adicionar Django REST Framework;
- não implementar integração real com TSE agora.

---

## Escopo atual do projeto

Este projeto é um sistema web simples de campanha, feito em Django, para cadastrar e organizar pessoas vinculadas a um responsável.

### Stack e arquitetura atual

- Backend: Django 5
- Banco de dados: SQLite
- Frontend: Django Templates + Tailwind CSS
- Build de assets: Node.js + Tailwind CLI
- Execução local/container: Docker Compose

### Objetivo atual do sistema

O sistema atualmente permite:

- cadastrar pessoas;
- editar pessoas;
- excluir pessoas;
- listar pessoas cadastradas;
- gerar relatório com filtros por responsável.

### App principal

O app principal se chama:

```txt
people
```

### Modelo principal atual

Existe um único modelo chamado `Person`.

Campos atuais:

- `full_name`: nome completo;
- `phone`: telefone, opcional;
- `local`: local da pessoa;
- `parent`: relação opcional para outra `Person`, usada como responsável.

Esse modelo cria uma estrutura auto-relacionada: uma pessoa pode ter outra pessoa como responsável.

### Regra de negócio atual importante

Uma pessoa não pode ser o próprio responsável.

Atualmente:

- no formulário de edição, o sistema remove a própria pessoa das opções de `parent`;
- existe validação adicional no backend para impedir essa situação.

### Rotas atuais

- `/` redireciona para `/people/`;
- `/people/` mostra a tela inicial do módulo;
- `/people/list/` mostra a lista de pessoas;
- `/people/new/` cria uma nova pessoa;
- `/people/edit/<id>/` edita uma pessoa;
- `/people/delete/<id>/` confirma e executa exclusão;
- `/people/relatorio/` mostra o relatório com filtros.

### Templates atuais

- `index.html`: página inicial com links para cadastro e relatório;
- `person_list.html`: tabela com pessoas cadastradas e ações de editar/excluir;
- `person_form.html`: formulário de criação/edição;
- `person_confirm_delete.html`: confirmação de exclusão;
- `person_report.html`: relatório com totais e filtro por responsável.

### Views atuais

- `index`: renderiza a página inicial;
- `person_list`: busca todas as pessoas e renderiza a listagem;
- `person_create`: processa criação via `PersonForm`;
- `person_update`: edita um registro existente;
- `person_delete`: exclui após confirmação;
- `person_report`:
  - carrega pessoas com `select_related("parent")`;
  - calcula total geral;
  - calcula total sem responsável;
  - monta opções de responsáveis que possuem vinculados;
  - permite filtrar:
    - todos;
    - sem responsável;
    - por um responsável específico.

### Relatório atual

O relatório exibe:

- total de pessoas cadastradas;
- total exibido no filtro atual;
- total de pessoas sem responsável;
- filtro por responsável;
- nome do filtro ativo.

### Formulário atual

O projeto usa `ModelForm`, chamado `PersonForm`.

Campos expostos atualmente:

- `full_name`;
- `phone`;
- `local`;
- `parent`.

Os widgets já vêm estilizados com classes do Tailwind.

### Admin

O modelo `Person` está registrado no Django Admin.

### Testes existentes

O projeto já possui testes para:

- listagem de pessoas;
- criação;
- edição;
- exclusão;
- validação para impedir auto-relacionamento;
- relatório com totais;
- filtro do relatório por responsável.

### Infra/Docker

- `Dockerfile` com dois estágios:
  - estágio Node para gerar `static/css/output.css`;
  - estágio Python para rodar a aplicação.
- `docker/entrypoint.sh` executa:
  - `python manage.py migrate --noinput`;
  - `python manage.py runserver 0.0.0.0:8000`.
- `docker-compose.yml` sobe um serviço `web` na porta `8000`.

### Observações técnicas

- O CSS do Tailwind é gerado no build.
- O banco é SQLite.
- Sem volume Docker, os dados podem não persistir entre recriações do container.
- O sistema é um CRUD simples com relatório.
- O sistema ainda não tem autenticação complexa.
- O sistema ainda não tem múltiplos apps de domínio.

---

## Direção desejada para evolução

O sistema deve evoluir para um software simples de gestão de campanha para vereador, focado em organização de apoiadores/pessoas e visualização básica de dados.

A evolução deve seguir os requisitos iniciais do software, mas adaptada ao estado atual do projeto.

Importante:

- não transformar o projeto em uma aplicação complexa;
- não adicionar múltiplos apps agora se não for necessário;
- não trocar SQLite agora;
- não criar API REST agora;
- não criar React/Vue/Next;
- não implementar mapa interativo agora;
- não implementar integração real com TSE agora;
- não coletar ou validar dados sensíveis sem aviso claro de consentimento.

---

## Regras de negócio prioritárias

O sistema deve evoluir primeiro em torno de perfis de acesso e visualização correta dos dados.

Os três graus de acesso são:

### Grau 1: Administradores

Perfis:

- candidato;
- coordenador de campanha.

Função:

- gestão completa da plataforma e da campanha.

Acesso esperado:

- acesso total a todas as funcionalidades;
- acesso a todos os cadastros;
- acesso a todos os relatórios;
- acesso a dashboards e visões consolidadas;
- sem limitação por responsável ou equipe.

### Grau 2: Gerentes de Equipe

Perfil típico:

- líderes comunitários.

Função:

- gestão da própria base de apoiadores e da rede vinculada ao seu núcleo.

Acesso esperado:

- acesso apenas aos dados da própria base;
- acesso apenas a relatórios relacionados à própria base;
- não devem enxergar a base de outros gerentes;
- podem visualizar as pessoas ligadas à sua hierarquia, mesmo quando o vínculo intermediário não for um gerente.

Regra importante:

- os gerentes de equipe são as pessoas que podem ter outras pessoas associadas a elas para fins de gestão de base;
- porém uma pessoa pode ter pessoas vinculadas a ela sem ser gerente formal;
- nesses casos, a ligação continua hierárquica e os registros ainda contam para o gerente de equipe que está acima dessa cadeia.

### Grau 3: Agentes de Cadastro

Função:

- cadastrar novos apoiadores.

Acesso esperado:

- permissão apenas para inserir novos dados;
- sem acesso à base completa;
- sem acesso a dados de outros usuários;
- sem acesso a relatórios;
- sem acesso a dashboards administrativos.

---

## Distinção importante: vínculo da pessoa x perfil de acesso

O projeto deve separar claramente dois conceitos:

- a hierarquia entre pessoas cadastradas no modelo `Person`;
- o nível de permissão do usuário logado.

Esses conceitos não são a mesma coisa.

Exemplo:

- uma pessoa cadastrada pode ter outras pessoas ligadas a ela no campo `parent`;
- isso não significa automaticamente que ela seja um gerente de equipe no sistema;
- por outro lado, a cadeia hierárquica dessas ligações deve ser considerada para compor a base visualizada pelo gerente responsável no topo daquela estrutura.

Em resumo:

- nem todo nó intermediário da árvore é gerente;
- mas a árvore inteira deve contar para o gerente responsável pela base;
- o ponto crítico do sistema é a visualização correta desses dados.

---

## Foco atual da evolução

Antes de enriquecer demais o modelo com novos campos, a prioridade funcional deve ser:

1. estruturar os níveis de acesso;
2. garantir a visibilidade correta por perfil;
3. preservar a hierarquia atual baseada em `parent`;
4. restringir relatórios e listagens conforme a base permitida para cada usuário;
5. manter o CRUD simples e utilizável no celular.

Campos eleitorais, dashboards sofisticados e integrações externas podem vir depois, desde que não atrapalhem essa base.

---

## Mudanças que devem ser feitas agora

Faça a atualização em passos pequenos.

Antes de editar, inspecione os arquivos atuais:

- models;
- forms;
- views;
- urls;
- templates;
- tests;
- admin;
- autenticação/permissões, se existirem;
- configurações de static/Tailwind se necessário.

Depois aplique as mudanças abaixo.

---

## 1. Introduzir níveis de acesso simples

O sistema ainda não possui autenticação complexa, então a evolução deve ser incremental.

Objetivo:

- preparar o projeto para suportar os três graus de acesso;
- evitar uma arquitetura pesada;
- manter a regra de negócio fácil de entender.

Direção sugerida:

- usar `User` do Django, se necessário;
- criar uma forma simples de associar o usuário a um grau de acesso;
- evitar ACL complexa, grupos excessivos ou múltiplos apps sem necessidade.

Os graus a suportar são:

- Grau 1: administrador;
- Grau 2: gerente de equipe;
- Grau 3: agente de cadastro.

Se for necessário criar um modelo de perfil simples, ele deve ser pequeno e direto.

---

## 2. Preservar e usar a hierarquia atual de `Person`

O projeto já usa `Person`, então não crie outro modelo principal agora.

A hierarquia atual com `parent` deve continuar existindo.

Regra central:

- uma pessoa pode estar ligada a outra pessoa;
- essa ligação compõe uma cadeia hierárquica;
- essa cadeia deve ser usada para definir quais registros entram na base de um gerente de equipe.

Importante:

- uma pessoa pode ter subordinados ou vinculados sem ser gerente formal;
- mesmo assim, esses registros devem contar para o gerente acima dela, quando houver.

Preserve a regra já existente:

- uma pessoa não pode ser o próprio responsável.

Se for necessário no futuro, a hierarquia pode ganhar regras extras, mas não complique isso agora.

---

## 3. Priorizar visualização correta dos dados

Este é o ponto mais importante da evolução atual.

O sistema deve passar a responder corretamente à pergunta:

```txt
Este usuário pode ver quais pessoas?
```

Regras esperadas:

- administradores veem tudo;
- gerentes de equipe veem apenas a própria base hierárquica;
- agentes de cadastro não veem bases alheias nem relatórios globais.

Para gerente de equipe, a base visível deve considerar:

- os registros cadastrados por ele, se esse conceito existir;
- as pessoas diretamente vinculadas a ele;
- as pessoas vinculadas em níveis abaixo da cadeia;
- os intermediários que não são gerentes formais, mas fazem parte da árvore.

Se houver conflito entre "quem cadastrou" e "a quem a pessoa está vinculada", a documentação e a implementação devem deixar explícito qual regra está valendo em cada tela.

Prioridade recomendada:

- usar a hierarquia como base principal da visualização;
- usar autoria de cadastro apenas se realmente necessário e bem definido.

---

## 4. Restringir listagem, relatório e dashboards por perfil

As telas existentes devem ser adaptadas sem reconstrução total.

Aplicar a regra de acesso principalmente em:

- `person_list`;
- `person_report`;
- futuras telas de dashboard, se surgirem.

Comportamento esperado:

- administrador: vê lista completa e relatório completo;
- gerente: vê apenas pessoas da sua base e relatórios da sua base;
- agente de cadastro: pode cadastrar, mas não deve ter acesso a relatório global nem à listagem ampla de dados.

Se for necessário esconder links, botões ou cards conforme o perfil, fazer isso de forma simples e previsível.

---

## 5. Ajustar a experiência por perfil

A interface deve refletir o que cada perfil realmente pode fazer.

Exemplos:

- administradores podem navegar por todas as áreas;
- gerentes de equipe devem enxergar apenas a gestão da própria base;
- agentes de cadastro devem cair em um fluxo enxuto de cadastro, sem excesso de informação.

O importante não é apenas bloquear ações no backend.

Também é importante:

- não confundir o usuário com telas que ele não pode usar;
- não exibir relatórios que ele não pode consultar;
- não expor totais globais para perfis restritos.

---

## 6. Manter a solução simples

Não transformar isso em um sistema corporativo pesado.

Evitar agora:

- regras excessivamente genéricas de autorização;
- arquitetura complexa de RBAC;
- múltiplos modelos novos sem necessidade;
- refatoração completa do CRUD atual.

A solução deve ser pequena, legível e incremental.

---

## 7. Testes

Atualize ou adicione testes coerentes com o que já existe.

Priorize testes para:

- administrador visualiza todos os registros;
- gerente visualiza apenas sua base;
- gerente não visualiza base de outro gerente;
- cadeia hierárquica conta para o gerente do topo, mesmo com intermediários não gerentes;
- agente de cadastro consegue inserir dados;
- agente de cadastro não acessa relatórios/listagens indevidas;
- auto-relacionamento continua impedido.

Não criar uma suíte enorme agora.

Mantenha os testes simples e orientados ao comportamento.

---

## 8. O que não fazer agora

Não fazer:

- criar app novo sem necessidade;
- trocar `Person` por outro modelo principal;
- apagar o CRUD atual;
- adicionar Django REST Framework;
- adicionar React, Vue, Next ou SPA;
- criar uma estrutura complexa de permissões sem necessidade;
- implementar dashboards sofisticados antes da regra de acesso estar correta;
- implementar scraping do TSE;
- integrar APIs externas não confirmadas;
- refatorar todo o projeto;
- mudar Docker sem necessidade;
- alterar nome de rotas existentes sem motivo;
- quebrar testes existentes sem atualizar adequadamente.

---

## Possível evolução futura, mas não implementar agora

Estes pontos podem ficar para uma próxima etapa:

- campos eleitorais adicionais no `Person`;
- consentimento detalhado e política LGPD mais completa;
- campo `created_by` ligando pessoa ao usuário que cadastrou;
- dashboard separado da tela de relatório;
- gráficos visuais;
- validação eleitoral real via fonte legal/oficial;
- PostgreSQL;
- deploy em produção;
- auditoria de alterações;
- importação de dados históricos.

---

## Resultado esperado desta tarefa

Ao final, o sistema deve continuar simples, mas com uma direção clara de controle de acesso e visualização hierárquica.

O resultado esperado é:

- CRUD atual preservado;
- hierarquia atual baseada em `parent` preservada;
- definição explícita dos 3 graus de acesso;
- base pronta para restringir visualização por perfil;
- relatórios e listagens preparados para escopo por usuário;
- distinção clara entre vínculo hierárquico e permissão;
- sem aumento desnecessário de complexidade.

---

## Instruções finais para o Codex

1. Primeiro leia a estrutura atual do projeto.
2. Não assuma arquivos que não existem.
3. Reuse o que já existe.
4. Faça mudanças pequenas e coerentes.
5. Preserve o estilo atual do código.
6. Preserve Django Templates + Tailwind.
7. Não crie frontend separado.
8. Não implemente TSE real agora.
9. Rode ou indique os comandos de teste.
10. Ao final, retorne um resumo com:
    - arquivos alterados;
    - migrations criadas;
    - testes adicionados/alterados;
    - como testar manualmente;
    - decisões tomadas.
