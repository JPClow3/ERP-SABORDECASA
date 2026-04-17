# Feature: Modelos de Produtos e Ficha Tecnica

## Objetivo

Definir os produtos vendidos e sua composicao padrao de insumos para suportar custo e baixa automatica de estoque.

## O que faz

Cria o model `Marmita` (Pequena, Media, Grande) e o model `ItemFichaTecnica`, relacionando `Insumo` com `Marmita` e quantidades padrao.

## Comandos pra IA

- Criar model `Marmita` com campos minimos para identificacao do produto e um campo `custo_estimado`.
- Criar model `ItemFichaTecnica` relacionando `Insumo` -> `Marmita` com quantidade_padrao.
- Utilizar **Django Lifecycle** para recalcular o `custo_estimado` da `Marmita` sempre que um `ItemFichaTecnica` for salvo ou alterado.
- Registrar `Marmita` e `ItemFichaTecnica` no `admin.py` utilizando **Django Unfold**.
- Garantir que a ficha tecnica seja facil de manter no painel administrativo via Inlines.
