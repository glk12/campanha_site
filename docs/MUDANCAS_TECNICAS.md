# Mudanças Técnicas — Módulo de Inteligência Territorial

Documento técnico das features/mudanças, por fase. Resumo do **o quê**,
**por quê** e **como**. Plano completo em
`requisitos/PLANO_MAPA_TERRITORIAL.md`.

Branch: `feat/modulo-mapa-territorial` (a partir de `main`/`0.1.0`),
entregue como **commit único** (squash — sem dados de máquina no
histórico). Stack mantida: Django 6 + Templates + Tailwind + SQLite
(decisão: opção híbrida — não migrar para React/FastAPI/PostGIS).

---

## chore: limpeza de versionamento

- **O quê:** removidos 31 arquivos `__pycache__/*.pyc` rastreados
  indevidamente; `.gitignore` ganhou `screenshots/`.
- **Por quê:** poluíam `git status`/diffs a cada execução.
- **Como:** `git rm -r --cached` dos arquivos.

---

## Fase A — Geolocalização no modelo

### O quê
`Person` ganhou 3 campos **opcionais**: `address` (CharField 255),
`latitude` e `longitude` (`DecimalField` 9,6, `null=True`).

### Por quê
O `requisitos.md` (seção 7, tabela `supporters`) exige `address/latitude/
longitude` para qualquer renderização geográfica. Campos opcionais = não
quebram registros nem fluxo existentes (seção 10: cadastro manual).

### Como
- `people/models.py`: campos entre `local` e `voting_city`.
- Migration `0005_person_address_person_latitude_person_longitude` —
  puramente aditiva (`AddField`), segura em base populada.
- `people/forms.py`: campos em `Meta.fields` + widgets (`NumberInput`
  `step="any"`), opcionais.
- `people/admin.py`: `latitude/longitude` em `list_display`, `address`
  em `search_fields`.
- `config/settings.py`: `CAMPAIGN_MUNICIPALITY = "Recife"`.

---

## Fase B — Mapa territorial

### O quê
Tela `/people/mapa/` (`dashboard_territorial`): mapa Leaflet com
contorno real do município, heatmap de apoiadores, clusters, camadas
toggleáveis, cards, filtros e ranking por zona.

### Decisão técnica crítica
O plano previa choropleth por polígono de zona eleitoral. **Não existe
dado público com a fronteira geográfica precisa de cada zona** — zona é
agrupamento administrativo, não recorte cartográfico. O repo
`mapaslivres/zonas-eleitorais` só tem CSV (zona→município).

**Solução adotada (validada com o usuário):**
- contorno **real** do município via malha oficial do **IBGE**
  (`servicodados.ibge.gov.br/api/v3/malhas/municipios/<cod>`);
- **heatmap** da concentração real de apoiadores (coords de `Person`);
- **clusters** de apoiadores reais;
- força por zona permanece como **tabela** (dado tabular é real).

### Como (backend — `people/views.py`)
- `dashboard_territorial`: `require_report_access` (admin/gerente;
  agente → 403). Escopo herdado de `get_visible_people_queryset`.
- Reaproveita `build_dashboard_context` — zero duplicação de agregação.
- Helpers: `normalize_zone`, `municipality_slug`, `_build_map_points`,
  `_zone_intensity_map`.
- `people/urls.py`: rota `mapa/` (nomes existentes intactos).

### Como (frontend — `dashboard_territorial.html`)
- Leaflet + `leaflet.heat` + `leaflet.markercluster` via **CDN**.
- Dados via `{{ ... | json_script }}` (sem XSS).
- Base OpenStreetMap (ruas); contorno IBGE tracejado; `L.heatLayer`;
  `L.markerClusterGroup`; `L.control.layers`.
- `static/geo/municipio_recife.geojson` (IBGE) + `static/geo/README.md`.
- Links "Mapa" em `base.html`/`index.html`, condicionais a relatórios.

### Armadilha encontrada e corrigida
`static/css/output.css` é **pré-compilado** (`npm run build-css`).
Classes Tailwind novas (ex.: `h-[460px]`) não existiam no CSS → mapa
invisível (altura zero). Corrigido recompilando; `output.css`
versionado precisa entrar (senão quebra no Docker).

Também: hash SRI do `leaflet.js` corrompido → SRI inválido removido.

---

## Fase C — Drill-down e crescimento

### O quê
- **Crescimento semanal**: total novo em 7 dias + por zona.
- **Drill-down** clicável: Município → Zona → Seções.

### Por quê
`requisitos.md` seção 3.1 (indicadores/ranking com crescimento) e 4.3
(drill-down Município→Zona→Seção).

### Como
- `build_dashboard_context`: `week_ago = now - 7d`; `zone_cards`
  ganham `growth_week` (agregação condicional
  `Count("id", filter=Q(created_at__gte=week_ago))`); novo
  `summary_growth_week`. Função compartilhada → relatório recebe as
  chaves (inofensivo).
- `dashboard_territorial`: `?zona=X` → `zone_sections` (seções da zona,
  no escopo do usuário) + `selected_zone`.
- Template: card de crescimento, coluna **Cresc. 7d**, zonas clicáveis,
  painel "Seções da zona X" com voltar.

---

## fix: destaque de página ativa no menu

- **Bug:** "Cadastrar" tinha `bg-blue-700` **hardcoded** e não havia
  lógica de página ativa — só ele parecia sempre azul.
- **Correção:** em `base.html`, `{% with cur=request.resolver_match.url_name %}`
  + classes `active`/`idle` por link. "Base" também acende em
  `person_update`/`person_delete`.

---

## chore: config de host/CSRF via variável de ambiente

- **O quê:** `ALLOWED_HOSTS` e `CSRF_TRUSTED_ORIGINS` vêm das env
  `DJANGO_ALLOWED_HOSTS` / `DJANGO_CSRF_TRUSTED_ORIGINS`. Sem env =
  só `localhost,127.0.0.1`. **Nenhum host de máquina versionado.**
- **Por quê:**
  1. Login via host externo:porta dava `403 CSRF (cookie not set)` —
     Django 6 exige origem declarada para POST de host externo.
  2. A máquina de dev é temporária; host/porta não podem ir
     versionados. Env vars resolvem na raiz (nada a apagar no push).
- **Como:** `config/settings.py` lê as env (split por vírgula). O dev
  server roda com as env setadas inline.

---

## Estado atual

| Item | Situação |
|------|----------|
| Testes | 23 verdes, 0 regressão |
| Fases A/B/C | ✅ implementadas |
| Fixes (menu, CSRF, config via env) | ✅ aplicados |
| Histórico | squashed em 1 commit limpo (sem host de máquina) |
| Dados demo | `db.sqlite3` local (fora do git), 16 apoiadores fictícios |
| Servidor | dev em host:porta efêmero (derrubar ao fim) |

### Pendências conhecidas (fora do escopo das fases A–C)
- Persistência Docker (sem volume → dados efêmeros no container).
- Porta no `docker-compose.yml` ainda `8000` (fora da convenção de dev).
- `DEBUG=True`, `SECRET_KEY` hardcoded — endurecimento de produção.
- Heatmap fraco com poucos dados (esperado; real com 2k–8k).
- GeoJSON por zona não existe (limitação de dado público, documentada).
