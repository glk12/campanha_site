# Plano de Implementação — Módulo de Inteligência Territorial / Mapa Eleitoral

> Decisão de produto: **opção 3 (híbrido pragmático)**. Mantém-se a stack atual
> (Django 6 + Templates + Tailwind + SQLite). Adiciona-se o mapa interativo —
> o diferencial estratégico do `requisitos.md` — com **Leaflet via CDN**, sem
> React, sem FastAPI, sem PostgreSQL/PostGIS nesta etapa.
>
> Justificativa do conflito CODEX × requisitos.md: o `requisitos.md` é o
> documento mais novo e específico e eleva o mapa a prioridade; o "não fazer
> mapa agora" do CODEX era uma decisão de *fase*, agora superada. As demais
> restrições do CODEX (não trocar stack, não overengineering, incremental)
> permanecem válidas e são respeitadas por este plano.

---

## Visão geral das fases

| Fase | Entrega | Arquivos tocados |
|------|---------|------------------|
| A | Dados geográficos no modelo + GeoJSON estático | models, forms, admin, migration, settings, static |
| B | Tela de mapa interativo (Leaflet) com heatmap por zona | views, urls, novo template, base.html, dashboard context |
| C | Drill-down Município→Zona→Seção + indicadores de crescimento | views, template |
| Testes | Cobertura de modelo, acesso e endpoint do mapa | tests.py |

Cada fase é independente, mergeável isolada, e não quebra os 16 testes atuais.

---

## FASE A — Habilitar dados geográficos

### A.1 Modelo `Person` (people/models.py)

Adicionar 3 campos opcionais (não quebram registros existentes):

```python
address = models.CharField(max_length=255, blank=True)
latitude = models.DecimalField(
    max_digits=9, decimal_places=6, null=True, blank=True
)
longitude = models.DecimalField(
    max_digits=9, decimal_places=6, null=True, blank=True
)
```

Justificativa: alinha `Person` à tabela `supporters` da seção 7 do
`requisitos.md` (`address, latitude, longitude`). `leader_id` já existe
como `parent`; `city` = `voting_city`; `status` = `voter_status`.

### A.2 Migration

Criar `people/migrations/0005_person_geolocation.py` via:

```bash
python manage.py makemigrations people
```

Todos os campos têm default vazio/null → migration sem `RunPython`, segura
em base populada.

### A.3 Formulário (people/forms.py)

- Adicionar `address`, `latitude`, `longitude` à `Meta.fields`.
- Widgets com `INPUT_CLASS` (padrão já existente no arquivo); lat/long como
  `NumberInput` com `step="any"`, `placeholder` explicativo.
- **Não** tornar obrigatórios — coords são opcionais no MVP (seção 10 do
  `requisitos.md`: "permitir cadastro manual, evitar dependência de
  integração automática").

### A.4 Admin (people/admin.py)

Adicionar `latitude`, `longitude` a `list_display` e `address` a
`search_fields` do `PersonAdmin`.

### A.5 GeoJSON das zonas eleitorais

- Definir município-alvo em `config/settings.py`:
  ```python
  CAMPAIGN_MUNICIPALITY = "Recife"   # ajustável por campanha
  ```
- Baixar o GeoJSON das zonas do município a partir de
  `github.com/mapaslivres/zonas-eleitorais` (fonte citada na seção 5.2.3 do
  `requisitos.md`) e salvar em
  `static/geo/zonas_<municipio>.geojson`.
- **Ponto crítico de integração:** `simulate_electoral_validation`
  (services.py) gera zonas `001`–`120` que **não correspondem** às zonas
  reais do GeoJSON. Tratamento no MVP:
  1. O heatmap casa `Person.electoral_zone` com a propriedade de zona da
     feature do GeoJSON (ex.: `feature.properties.zona`), normalizando ambos
     com `str(...).lstrip("0")`.
  2. Zonas sem correspondência ainda aparecem como polígono cinza (sem
     intensidade) — degradação graciosa, sem erro.
  3. Criar management command `seed_demo_territorial` que popula apoiadores
     de exemplo usando números de zona reais do GeoJSON, para demonstração.

**Saída da Fase A:** modelo e formulário preparados; nenhuma UI nova ainda;
testes atuais continuam verdes.

---

## FASE B — Mapa interativo (Leaflet)

### B.1 View `dashboard_territorial` (people/views.py)

```python
@login_required
def dashboard_territorial(request):
    profile = require_report_access(request.user)   # admin + manager; agente → 403
    base_people = get_visible_people_queryset(request.user).select_related("parent")
    filtered_people, filter_data = apply_people_filters(base_people, request)
    context = get_common_context(profile)
    context.update(build_dashboard_context(base_people, filtered_people, profile))
    context.update({
        "geojson_url": static("geo/zonas_recife.geojson"),
        "map_points": _build_map_points(filtered_people),  # só quem tem lat/long
        "zone_intensity": _zone_intensity_map(context["zone_cards"]),
        "filter_data": filter_data,
    })
    return render(request, "people/dashboard_territorial.html", context)
```

- Reaproveita `build_dashboard_context` (já calcula `intensity` por zona —
  views.py:154-161). **Zero duplicação de lógica de agregação.**
- Respeita escopo por perfil automaticamente via
  `get_visible_people_queryset` (gerente só vê sua hierarquia no mapa).
- Helpers novos e pequenos:
  - `_build_map_points`: lista de `{lat, lng, name, zone, status}` apenas
    para `Person` com `latitude`/`longitude` preenchidos.
  - `_zone_intensity_map`: `{ "101": 87, ... }` a partir de `zone_cards`.

### B.2 URL (people/urls.py)

```python
path("mapa/", dashboard_territorial, name="dashboard_territorial"),
```

Rota nova, **não altera nomes existentes** (regra do CODEX respeitada).

### B.3 Template `people/dashboard_territorial.html`

- Estende `people/base.html`.
- Leaflet por **CDN** (sem alterar `requirements.txt` nem o build Tailwind):
  ```html
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  ```
- Dados passados ao JS de forma segura via `{{ ... | json_script }}`
  (sem montar JSON na mão, sem XSS).
- Camadas (seção 4.2 do `requisitos.md`) com toggles `L.control.layers`:
  - polígonos das zonas (choropleth);
  - marcadores de apoiadores (com `markercluster` opcional, CDN);
  - locais de votação (fase futura — placeholder).
- Heatmap por escala de cor da seção 4.1:
  - verde (forte) ≥ 66, amarelo (intermediária) 33–65, vermelho (fraca) < 33
  — usando o `intensity` 20–100 já calculado.
- Painel de indicadores rápidos (seção 3.1) reusando `summary_*` do contexto:
  total, aptos, validados, com consentimento, zonas fortes/fracas.
- Painel de filtros reusa `apply_people_filters` (status, zona, busca) —
  filtros já existentes, sem reescrever.

### B.4 Navegação (people/templates/people/base.html e index.html)

- Adicionar link "Mapa" na `<nav>` (base.html ~linha 69), visível só quando
  `can_view_reports` (mesma condição do link "Relatorio").
- Adicionar card "Mapa territorial" no `index.html` (~linha 74), condicional
  ao perfil.

**Saída da Fase B:** mapa funcional com zonas coloridas + apoiadores
geolocalizados, restrito por perfil. Diferencial estratégico entregue.

---

## FASE C — Drill-down e indicadores de crescimento

### C.1 Drill-down (seção 4.3)

Navegação `Município → Zona → Seção → Apoiadores` sobre os agregados que
**já existem** em `build_dashboard_context`:

- Clique em zona no mapa → filtra `?zona=NNN` (reusa `apply_people_filters`).
- Tabela "Ranking territorial" (seção 3.1): `| Zona | Apoiadores |
  Crescimento | Potencial |` a partir de `zone_cards` + métrica de
  crescimento (C.2).
- Sem novas views — apenas querystring + render condicional no template.

### C.2 Indicadores de crescimento

`Person.created_at` já existe (migration 0004). Adicionar a
`build_dashboard_context`:

```python
from django.utils import timezone
from datetime import timedelta
week_ago = timezone.now() - timedelta(days=7)
"summary_growth_week": base_people.filter(created_at__gte=week_ago).count(),
```

E crescimento por zona (subquery `Count` filtrado por `created_at`) para
preencher a coluna "Crescimento" do ranking. Mudança localizada numa função
já existente.

**Saída da Fase C:** drill-down navegável + métricas de crescimento semanal
e potencial por zona.

---

## Testes (people/tests.py)

Adicionar à suíte existente (mantendo estilo orientado a comportamento):

| Teste | Verifica |
|-------|----------|
| `test_person_accepts_geolocation` | salvar `Person` com lat/long válidos |
| `test_form_geolocation_optional` | criar sem coords continua válido |
| `test_territorial_map_renders_for_admin` | 200 + contexto `map_points`/`zone_intensity` |
| `test_territorial_map_scoped_for_manager` | gerente só vê pontos da própria hierarquia |
| `test_territorial_map_forbidden_for_agent` | agente → 403 (igual a relatório) |
| `test_zone_intensity_color_thresholds` | mapeamento intensidade→cor correto |
| `test_growth_week_metric` | `summary_growth_week` conta últimos 7 dias |

Rodar:
```bash
python manage.py test people
```

Critério de aceite: **23 testes verdes** (16 atuais + 7 novos), 0 regressões.

---

## Itens explicitamente FORA deste plano (Fases 2/3 do requisitos.md)

- Ingestão automática de dados do TSE (seção 5.1) — `ElectionHistory`
  continua manual/import via admin.
- Validação eleitoral real via CPF (seção 10 confirma: adiar).
- Mapa operacional de campo: geolocalização em tempo real, check-in,
  roteirização (seção 3.4) — Fase 3.
- IA territorial / previsão eleitoral (seção 12, Etapa 5).
- Migração para PostgreSQL/PostGIS — só se a escala (>8.000) ou consultas
  espaciais server-side exigirem; hoje GeoJSON client-side basta.
- Logs de auditoria / criptografia / HTTPS (seção 9) — endurecimento de
  produção, trilha separada (`DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS`).

---

## Resumo de impacto

| Arquivo | Mudança | Risco |
|---------|---------|-------|
| `people/models.py` | +3 campos opcionais | baixo |
| `people/migrations/0005_*` | nova migration aditiva | baixo |
| `people/forms.py` | +3 campos no form | baixo |
| `people/admin.py` | display/search | nenhum |
| `people/views.py` | +1 view, +2 helpers, +métrica em função existente | baixo |
| `people/urls.py` | +1 rota nova | nenhum |
| `people/templates/people/dashboard_territorial.html` | novo | baixo |
| `people/templates/people/base.html` / `index.html` | +1 link/card condicional | baixo |
| `config/settings.py` | +`CAMPAIGN_MUNICIPALITY` | nenhum |
| `static/geo/zonas_*.geojson` | novo asset estático | nenhum |
| `people/tests.py` | +7 testes | nenhum |

Sem novas dependências Python. Leaflet via CDN. Build Tailwind inalterado.
CRUD, autenticação, hierarquia e testes atuais preservados.

## Ordem de execução recomendada

1. Fase A (modelo + migration + form) → rodar testes (devem continuar 16✅).
2. Baixar/validar GeoJSON do município + command de seed demo.
3. Fase B (view + url + template + nav) → testes de mapa.
4. Fase C (drill-down + crescimento) → testes de métrica.
5. Revisão final + `python manage.py test people` + checagem manual mobile.
