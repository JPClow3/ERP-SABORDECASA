from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from estoque.models import MovimentoEstoque
from estoque.services import registrar_resultado_producao, registrar_saida_estoque
from .models import RegistroProducao, RegistroProducaoItem


def _decimal(value):
    return Decimal(str(value))


def registrar_producao(*, produto, quantidade_produzida, quantidades_reais=None, observacao=""):
    quantidade_produzida = _decimal(quantidade_produzida)
    if quantidade_produzida <= Decimal("0.000"):
        raise ValidationError("A quantidade produzida deve ser maior que zero.")

    itens_ficha = list(produto.itens_ficha.select_related("item"))
    if not itens_ficha:
        raise ValidationError("O produto precisa de uma ficha tecnica antes da producao.")

    quantidades_reais = quantidades_reais or {}

    with transaction.atomic():
        registro = RegistroProducao.objects.create(
            produto=produto,
            quantidade_produzida=quantidade_produzida,
            observacao=observacao or "",
        )

        custo_total = Decimal("0.0000")
        for ficha in itens_ficha:
            quantidade = _decimal(
                quantidades_reais.get(ficha.item_id, quantidades_reais.get(str(ficha.item_id), ficha.quantidade_padrao * quantidade_produzida))
            )
            movimento = registrar_saida_estoque(
                item=ficha.item,
                quantidade=quantidade,
                tipo=MovimentoEstoque.Tipo.PRODUCAO_CONSUMO,
                documento=f"producao:{registro.pk}",
                observacao=f"Producao de {produto.nome}",
            )
            RegistroProducaoItem.objects.create(
                registro=registro,
                item=ficha.item,
                quantidade_utilizada=quantidade,
                custo_unitario=movimento.custo_unitario,
                custo_total=movimento.custo_total,
            )
            custo_total += movimento.custo_total

        custo_unitario = custo_total / quantidade_produzida
        registro.custo_total = custo_total
        registro.custo_unitario = custo_unitario
        registro.save(update_fields=["custo_total", "custo_unitario"])

        registrar_resultado_producao(
            item=produto.item_estoque,
            quantidade=quantidade_produzida,
            custo_unitario=custo_unitario,
            documento=f"producao:{registro.pk}",
            observacao=f"Producao de {produto.nome}",
        )
        produto.recalcular_custo_estimado()
        return registro
