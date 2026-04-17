# Feature: Modelos de Estoque de Insumos

## Objetivo

Estruturar a base de dados de insumos para registrar tudo o que entra na cozinha e viabilizar calculos de custo.

## O que faz

Cria o model `Insumo` com nome, unidade de medida e custo atual, e disponibiliza o cadastro no Django Admin.

## Comandos pra IA

- Criar o model `Insumo` com campos: nome, unidade_medida, custo_atual.
- Registrar `Insumo` em `admin.py` utilizando **Django Unfold** e **Django Import-Export** para permitir carga em massa de insumos.
- Preparar para cadastro via painel nativo do Django (ex.: Arroz, Feijao, Carne).
