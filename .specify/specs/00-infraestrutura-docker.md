# Feature: Setup do Ambiente Docker

## Objetivo
Criar o arquivo `docker-compose.yml` para desenvolvimento local, subindo o banco de dados PostgreSQL e a aplicação Django.

## Requisitos do Compose
1. Crie um serviço `db` usando a imagem `postgres:15-alpine`.
2. Configure as variáveis de ambiente padrão do Postgres (POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB) lendo de um arquivo `.env`.
3. Crie um volume nomeado `postgres_data` e mapeie para `/var/lib/postgresql/data` no serviço `db` para persistir os dados.
4. Crie o serviço `web` rodando o servidor de desenvolvimento do Django (`python manage.py runserver 0.0.0.0:8000`).
5. O serviço `web` deve depender do serviço `db` (`depends_on`).
6. Mapeie a porta 8000 do host para a porta 8000 do container.
7. Monte o volume do código fonte para permitir o hot-reload durante o desenvolvimento.
