# campanha_site

Aplicação Django para uma campanha eleitoral, começando com o módulo de cadastro de pessoas.

## Como rodar o projeto

### 1. Criar e ativar o ambiente virtual

```bash
python -m venv .venv
source .venv/bin/activate
```

No Windows:

```bash
.venv\Scripts\activate
```

### 2. Instalar as dependências do Python

```bash
pip install -r requirements.txt
```

### 3. Instalar as dependências do Tailwind

```bash
npm install
```

### 4. Aplicar as migrations

```bash
python manage.py migrate
```

### 5. Gerar o CSS do Tailwind

```bash
npm run build-css
```

Se quiser acompanhar alterações de estilo em tempo real:

```bash
npm run watch-css
```

### 6. Rodar o servidor Django

```bash
python manage.py runserver
```

Depois, acesse:

- `http://127.0.0.1:8000/people/`

## Estrutura atual

- `config/`: configurações do projeto Django
- `people/`: app responsável pelo cadastro de pessoas
- `people/templates/people/`: templates do módulo
- `static/`: arquivos estáticos, incluindo o CSS gerado pelo Tailwind

## Observações

- O banco usado no momento é SQLite.
- Sempre que alterar classes do Tailwind nos templates, rode `npm run build-css` novamente (a nao ser que esteja usando o watch-css).
