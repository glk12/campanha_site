# Sistema de Gestão de Campanha Eleitoral

## Especificação Técnica — Módulo de Inteligência Territorial e Mapa Eleitoral

---

# 1. Visão Geral do Projeto

O sistema será uma plataforma de gestão de campanha eleitoral focada inicialmente em campanhas municipais para vereador, com ênfase em inteligência territorial, organização da base de apoiadores e análise geográfica de desempenho eleitoral.

O objetivo principal é permitir que a equipe de campanha visualize estrategicamente:

* concentração de apoiadores;
* desempenho eleitoral histórico;
* zonas eleitorais fortes e fracas;
* evolução territorial da campanha;
* oportunidades de crescimento.

A principal funcionalidade diferenciadora do sistema será o módulo de mapa eleitoral interativo.

---

# 2. Objetivos do Módulo de Mapa

O módulo deverá permitir:

* visualizar zonas eleitorais;
* visualizar seções eleitorais;
* identificar regiões fortes/fracas;
* exibir apoiadores geograficamente;
* gerar heatmaps eleitorais;
* cruzar dados históricos do TSE;
* auxiliar decisões estratégicas de campanha;
* otimizar ações de campo.

---

# 3. Escopo Funcional

---

## 3.1 Dashboard Territorial

### Objetivo

Tela principal de análise geográfica da campanha.

---

### Componentes

#### Painel de filtros

Filtros disponíveis:

* Município
* Zona eleitoral
* Seção eleitoral
* Bairro
* Líder comunitário
* Status eleitoral
* Data de cadastro
* Região
* Grau de apoio

---

#### Mapa interativo

O mapa deverá exibir:

* polígonos das zonas eleitorais;
* polígonos das seções eleitorais;
* apoiadores cadastrados;
* heatmap de apoio;
* intensidade eleitoral;
* locais de votação.

---

#### Indicadores rápidos

Exibir:

* total de apoiadores;
* apoiadores aptos;
* crescimento semanal;
* zonas fortes;
* zonas fracas;
* cobertura territorial;
* potencial eleitoral.

---

#### Ranking territorial

Tabela dinâmica:

| Zona | Apoiadores | Crescimento | Potencial |
| ---- | ---------- | ----------- | --------- |

---

## 3.2 Tela de Zona Eleitoral

### Objetivo

Análise detalhada de cada zona eleitoral.

---

### Informações exibidas

* número da zona;
* município;
* total de eleitores;
* apoiadores cadastrados;
* percentual de cobertura;
* votação histórica;
* crescimento da base;
* líderes responsáveis.

---

### Gráficos

* evolução temporal;
* distribuição por bairro;
* crescimento semanal;
* comparação histórica.

---

### Mapa interno

Visualização:

* seções eleitorais;
* bairros;
* concentração de apoiadores;
* intensidade de apoio.

---

## 3.3 Tela de Seção Eleitoral

### Objetivo

Análise operacional de microterritórios.

---

### Informações

* seção eleitoral;
* local de votação;
* total de eleitores;
* apoiadores cadastrados;
* responsável territorial;
* taxa de cobertura;
* ações realizadas.

---

## 3.4 Mapa Operacional de Campo

### Objetivo

Uso mobile pela equipe em ações presenciais.

---

### Funcionalidades

* geolocalização;
* check-in;
* roteirização;
* registro de visitas;
* atualização em tempo real;
* acompanhamento de ações de campo.

---

# 4. Funcionalidades Técnicas

---

## 4.1 Heatmap Eleitoral

O sistema deverá colorir automaticamente as regiões conforme indicadores estratégicos.

---

### Critérios possíveis

* quantidade de apoiadores;
* votação histórica;
* crescimento;
* potencial eleitoral;
* taxa de conversão.

---

### Escala visual

| Cor      | Significado          |
| -------- | -------------------- |
| Verde    | Região forte         |
| Amarelo  | Região intermediária |
| Vermelho | Região fraca         |

---

## 4.2 Camadas do Mapa

O usuário poderá ativar/desativar:

* zonas eleitorais;
* seções eleitorais;
* bairros;
* apoiadores;
* locais de votação;
* lideranças;
* eventos;
* ações de campanha.

---

## 4.3 Drill-down Territorial

Estrutura de navegação:

```txt
Município
  ↓
Zona Eleitoral
  ↓
Seção Eleitoral
  ↓
Apoiadores
```

---

## 4.4 Busca Inteligente

Busca por:

* CPF;
* nome;
* telefone;
* zona;
* seção;
* bairro;
* endereço.

---

# 5. Dados Necessários

---

## 5.1 Dados Eleitorais

### Fontes

#### Tribunal Superior Eleitoral (TSE)

Dados públicos:

* resultados eleitorais;
* votação por seção;
* votação por zona;
* eleitorado;
* locais de votação.

Portal oficial:
[https://dadosabertos.tse.jus.br/](https://dadosabertos.tse.jus.br/)

---

## 5.2 Dados Geográficos

### Formatos suportados

* GeoJSON
* Shapefile
* TopoJSON

---

### Dados necessários

* limites das zonas eleitorais;
* limites das seções;
* municípios;
* bairros;
* coordenadas geográficas.

---

### Fontes

#### IBGE

[https://www.ibge.gov.br/](https://www.ibge.gov.br/)

#### Repositórios públicos GeoJSON

[https://github.com/mapaslivres/zonas-eleitorais](https://github.com/mapaslivres/zonas-eleitorais)

---

## 5.3 Dados Internos do Sistema

### Cadastro de apoiadores

Campos principais:

```txt
- nome
- cpf
- telefone
- endereço
- latitude
- longitude
- zona eleitoral
- seção eleitoral
- município
- líder responsável
- status
- observações
```

---

# 6. Arquitetura Recomendada

---

# Backend

## Recomendado

### FastAPI

ou

### NestJS

---

# Banco de Dados

## PostgreSQL

---

## Extensão Geográfica

### PostGIS

Responsável por:

* consultas espaciais;
* interseção geográfica;
* filtros territoriais;
* cálculo de distância;
* manipulação de polígonos.

---

# Frontend

## Recomendado

### React

---

## Biblioteca de mapas

### Opção recomendada

#### Mapbox

Vantagens:

* alta performance;
* visual moderno;
* heatmaps;
* clusterização;
* ótima experiência visual.

---

### Alternativa

#### Leaflet

Vantagens:

* simples;
* leve;
* fácil integração.

---

# Bibliotecas de Dashboard

* Apache ECharts
* Recharts

---

# 7. Modelagem Inicial do Banco

---

## Tabela: supporters

```sql
id
name
cpf
phone
address
latitude
longitude
electoral_zone
electoral_section
city
leader_id
created_at
```

---

## Tabela: electoral_zones

```sql
id
zone_number
city
geometry
total_voters
historical_votes
```

---

## Tabela: electoral_sections

```sql
id
section_number
zone_id
location_name
geometry
```

---

# 8. Estratégia de MVP

---

# MVP Fase 1

Implementar:

* cadastro de apoiadores;
* mapa básico;
* zonas eleitorais;
* heatmap;
* dashboards;
* filtros básicos.

---

# MVP Fase 2

Adicionar:

* seções eleitorais;
* dados históricos;
* BI territorial;
* relatórios avançados.

---

# MVP Fase 3

Adicionar:

* IA territorial;
* previsão eleitoral;
* automações;
* aplicativo mobile.

---

# 9. Segurança e LGPD

O sistema lidará com:

* CPF;
* dados eleitorais;
* geolocalização;
* dados políticos.

Essas informações são sensíveis e exigem tratamento adequado.

---

## Medidas obrigatórias

* HTTPS;
* criptografia;
* controle hierárquico;
* logs de auditoria;
* consentimento explícito;
* política de retenção;
* autenticação segura.

---

## Controle de acesso

### Administrador

Acesso total.

### Líder comunitário

Acesso apenas à própria base.

### Agente

Somente cadastro.

---

# 10. Validação Técnica dos Dados

---

## Dados que já podem ser obtidos

### Disponíveis publicamente

* votação por zona;
* votação por seção;
* eleitorado;
* resultados históricos;
* dados geográficos.

---

## Parte crítica

A validação automática da situação eleitoral via CPF pode apresentar:

* limitações legais;
* CAPTCHA;
* ausência de API pública oficial;
* restrições do TSE.

---

## Recomendação inicial

No MVP:

* permitir cadastro manual de zona/seção;
* evitar dependência de integração automática;
* focar inicialmente em CRM + inteligência territorial.

---

# 11. Objetivo Estratégico do Produto

O sistema não deve ser tratado apenas como:

* um cadastro de eleitores;
* um validador de CPF.

O verdadeiro diferencial é:

```txt
INTELIGÊNCIA TERRITORIAL ELEITORAL
```

Ou seja:

* análise geográfica;
* gestão territorial;
* heatmaps;
* cruzamento de dados;
* operação estratégica de campanha.

---

# 12. Roadmap Recomendado

---

## Etapa 1

* Renderizar zonas eleitorais no mapa.

---

## Etapa 2

* Integrar dados históricos do TSE.

---

## Etapa 3

* Implementar dashboards analíticos.

---

## Etapa 4

* Adicionar mobile e operações de campo.

---

## Etapa 5

* Inteligência artificial e previsões eleitorais.

---

# 13. Tecnologias Recomendadas

| Camada    | Tecnologia       |
| --------- | ---------------- |
| Frontend  | React            |
| Mapas     | Mapbox / Leaflet |
| Backend   | FastAPI / NestJS |
| Banco     | PostgreSQL       |
| GIS       | PostGIS          |
| Dashboard | Apache ECharts   |
| Mobile    | React Native     |
| Cache     | Redis            |

---

# 14. Conclusão

O projeto possui alta viabilidade técnica para construção de um MVP robusto focado em:

* visualização territorial;
* análise eleitoral;
* CRM de campanha;
* inteligência geográfica.

A principal recomendação é iniciar pelo núcleo mais valioso do produto:

* mapa;
* heatmaps;
* cruzamento territorial;
* dashboards;
* histórico eleitoral.

E deixar integrações automatizadas mais sensíveis (como validação eleitoral via CPF) para fases posteriores.;