# Feature: Controle de Vendas e Baixa Automatica

## Objetivo

Registrar vendas do dia de forma rapida e refletir automaticamente o consumo de estoque com base na ficha tecnica.

## O que faz

Cria tela com botoes de venda por tipo de marmita; cada clique registra uma `Venda` e executa rotina de baixa proporcional de insumos.

## Comandos pra IA

- Criar model `Venda` com relacionamento com `Marmita`, quantidade e data/hora.
- Criar tela operacional com botoes grandes para vendas rapidas (ex.: Marmita M, Marmita G).
- Processar clique via HTMX para registrar venda sem reload.
- Implementar funcao de baixa no estoque baseada nos itens da ficha tecnica.
