# GeoJSON do mapa territorial

## municipio_recife.geojson

Contorno **real** do município de Recife, obtido da malha oficial do IBGE:

    https://servicodados.ibge.gov.br/api/v3/malhas/municipios/2611606?formato=application/vnd.geo+json&qualidade=maxima

(`2611606` = código IBGE de Recife.)

### Por que não há polígono por zona eleitoral

Zona eleitoral é um agrupamento administrativo de eleitores/seções, **não**
um recorte geográfico oficial. Não existe dado público com a fronteira
precisa de cada zona dentro de uma cidade. Por isso o mapa usa:

- **contorno real do município** (este arquivo, IBGE);
- **mapa de calor** da concentração real de apoiadores (coordenadas
  lat/long de `Person`);
- **clusters** dos apoiadores reais.

A força por zona continua disponível, mas como **tabela** (ranking
territorial), que é dado tabular real — não um polígono inventado.

### Trocar de município

1. Descobrir o código IBGE do município-alvo.
2. Baixar a malha:
   `.../malhas/municipios/<CODIGO>?formato=application/vnd.geo+json&qualidade=maxima`
3. Salvar como `municipio_<slug>.geojson` (slug = nome sem acento, minúsculo).
4. Apontar `CAMPAIGN_MUNICIPALITY` em `config/settings.py`.

O nome do arquivo é derivado de `CAMPAIGN_MUNICIPALITY` na view
`dashboard_territorial` (`municipio_<slug>.geojson`).
