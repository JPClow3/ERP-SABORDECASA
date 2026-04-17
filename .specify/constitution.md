# Constituição do Projeto: Sistema Marmitaria

## 1. Stack Tecnológica Obrigatória
- **Backend:** Python 3.12+ com Django 5+.
- **Frontend:** HTML Renderizado no servidor (Django Templates) com **Django Unfold** para o Admin.
- **Bibliotecas Core:** `django-import-export`, `django-lifecycle`, `django-widget-tweaks`, `django-environ`, `django-extensions`.
- **Reatividade:** HTMX (com `django-htmx`) e Alpine.js.
- **Estilização:** Tailwind CSS (via `django-tailwind`).
- **Banco de Dados:** PostgreSQL (obrigatório para desenvolvimento e produção).

## 2. Regras de Arquitetura Django
- **PROIBIDO** o uso de Django REST Framework (DRF) ou qualquer stack de SPA (Single Page Application). Tudo deve ser resolvido via HTMX trocando pedaços do HTML.
- Mantenha a lógica de negócios pesada (como cálculos de rendimento de insumos) nos `Models` ou em arquivos `services.py`, mantendo as `Views` magras.
- Use Function-Based Views (FBVs) para rotas que respondem a requisições HTMX, retornando apenas fragmentos HTML (`render(request, 'partials/sua_div.html')`).

## 3. Padrões de Deploy e Infraestrutura
- A aplicação será servida via Gunicorn.
- O ambiente deve ser preparado para rodar em containers Docker, utilizando Nginx como proxy reverso para servir arquivos estáticos.
