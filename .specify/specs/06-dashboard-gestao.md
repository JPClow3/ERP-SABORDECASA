# Feature: Dashboard de Fechamento Diario

## Objetivo

Entregar visao resumida do resultado diario para tomada de decisao rapida.

## O que faz

Cria a home (`/`) com cards de indicadores principais: vendas do dia, custo de producao e margem estimada de lucro.

## Comandos pra IA

- Criar view inicial com os indicadores: Vendas do Dia (R$), Custo de Producao (R$), Margem de Lucro Estimada (%).
- Exibir os indicadores em 3 cards simples no dashboard.
- Aplicar destaque visual em vermelho com Tailwind quando margem < 30%.
- Manter implementacao com Django Templates + HTMX (sem API REST).
