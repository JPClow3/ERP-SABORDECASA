# Feature: Produção e Cálculo de Rendimento (Tela Ouro)

## Objetivo

Permitir o lancamento rapido de producao para calcular rendimento real e custo por marmita sem recarregar a pagina.

## O que faz

Cria interface em HTMX onde o usuario informa o insumo bruto utilizado e a quantidade produzida; a view calcula custo por marmita e injeta o resultado parcial em tempo real.

## Modelagem de Dados

Crie ou atualize os seguintes models no app `producao`:

1. `Insumo`: nome (char), unidade_medida (char), preco_atual_kg (decimal).
2. `ProducaoDiaria`: insumo (FK), peso_bruto_utilizado (decimal), marmitas_produzidas (inteiro), custo_por_marmita_calculado (decimal), data (date).

## Comportamento da Interface (HTMX)

- Crie um formulario no template `lancamento.html` com os campos: Insumo (Select), Peso Bruto (Input Number) e Marmitas Produzidas (Input Number).
- Ao digitar no campo "Marmitas Produzidas" (evento `hx-trigger="keyup changed delay:500ms"`), o formulario deve fazer um `hx-post` para a view `calcular_rendimento_parcial`.
- A view deve calcular `(peso_bruto_utilizado * insumo.preco_atual_kg) / marmitas_produzidas`.
- A view deve retornar um fragmento HTML atualizando a div `#resultado-calculo` com o custo calculado, alertando em vermelho (Tailwind `text-red-600`) se o custo passar de R$ 6,00.

## Comandos pra IA

- Criar tela de lancamento com campos de insumo, peso bruto e marmitas produzidas.
- Implementar `hx-post` para calculo parcial via FBV.
- Aplicar formula de rendimento/custo na view e retornar fragmento HTML.
- Atualizar resultado na tela sem reload completo.
- Persistir o lancamento em `ProducaoDiaria` ao submeter o formulario principal.
