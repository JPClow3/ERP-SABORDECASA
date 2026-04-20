from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from .models import EntradaMercadoria, ItemEntradaMercadoria, ItemEstoque, MovimentoEstoque


QTD_ZERO = Decimal("0.000")


def _decimal(value):
    return Decimal(str(value))


def _validar_quantidade(quantidade):
    quantidade = _decimal(quantidade)
    if quantidade <= QTD_ZERO:
        raise ValidationError("A quantidade deve ser maior que zero.")
    return quantidade


def _bloquear_item(item):
    return ItemEstoque.objects.select_for_update().get(pk=item.pk)


def registrar_entrada_mercadoria(*, itens, fornecedor="", data=None, observacao=""):
    if not itens:
        raise ValidationError("Informe pelo menos um item para entrada.")

    with transaction.atomic():
        entrada = EntradaMercadoria.objects.create(
            fornecedor=fornecedor or "",
            observacao=observacao or "",
            **({"data": data} if data else {}),
        )

        for item_data in itens:
            item = _bloquear_item(item_data["item"])
            quantidade = _validar_quantidade(item_data["quantidade"])
            preco_unitario = _decimal(item_data["preco_unitario"])
            if preco_unitario < Decimal("0.0000"):
                raise ValidationError("O preco unitario nao pode ser negativo.")

            saldo_anterior = item.saldo_atual
            custo_total_anterior = saldo_anterior * item.custo_medio
            custo_total_entrada = quantidade * preco_unitario
            saldo_posterior = saldo_anterior + quantidade
            custo_medio = (
                (custo_total_anterior + custo_total_entrada) / saldo_posterior
                if saldo_posterior > QTD_ZERO
                else Decimal("0.0000")
            )

            ItemEntradaMercadoria.objects.create(
                entrada=entrada,
                item=item,
                quantidade=quantidade,
                preco_unitario=preco_unitario,
                custo_total=custo_total_entrada,
            )

            item.saldo_atual = saldo_posterior
            item.custo_medio = custo_medio
            item.ultimo_preco_pago = preco_unitario
            item.save(update_fields=["saldo_atual", "custo_medio", "ultimo_preco_pago", "atualizado_em"])

            MovimentoEstoque.objects.create(
                item=item,
                tipo=MovimentoEstoque.Tipo.ENTRADA,
                quantidade=quantidade,
                custo_unitario=preco_unitario,
                custo_total=custo_total_entrada,
                saldo_anterior=saldo_anterior,
                saldo_posterior=saldo_posterior,
                documento=f"entrada:{entrada.pk}",
                observacao=observacao or "",
            )

        return entrada


def registrar_saida_estoque(*, item, quantidade, tipo, observacao="", documento=""):
    if tipo not in {
        MovimentoEstoque.Tipo.SAIDA,
        MovimentoEstoque.Tipo.PERDA_TECNICA,
        MovimentoEstoque.Tipo.PRODUCAO_CONSUMO,
    }:
        raise ValidationError("Tipo de saida de estoque invalido.")

    with transaction.atomic():
        item = _bloquear_item(item)
        quantidade = _validar_quantidade(quantidade)
        if item.saldo_atual < quantidade:
            raise ValidationError(f"Saldo insuficiente para {item.nome}.")

        saldo_anterior = item.saldo_atual
        saldo_posterior = saldo_anterior - quantidade
        custo_unitario = item.custo_medio
        custo_total = quantidade * custo_unitario

        item.saldo_atual = saldo_posterior
        item.save(update_fields=["saldo_atual", "atualizado_em"])

        return MovimentoEstoque.objects.create(
            item=item,
            tipo=tipo,
            quantidade=quantidade,
            custo_unitario=custo_unitario,
            custo_total=custo_total,
            saldo_anterior=saldo_anterior,
            saldo_posterior=saldo_posterior,
            documento=documento,
            observacao=observacao or "",
        )


def registrar_perda_tecnica(*, item, quantidade, observacao=""):
    return registrar_saida_estoque(
        item=item,
        quantidade=quantidade,
        tipo=MovimentoEstoque.Tipo.PERDA_TECNICA,
        observacao=observacao,
    )


def registrar_resultado_producao(*, item, quantidade, custo_unitario, documento="", observacao=""):
    with transaction.atomic():
        item = _bloquear_item(item)
        quantidade = _validar_quantidade(quantidade)
        custo_unitario = _decimal(custo_unitario)
        if custo_unitario < Decimal("0.0000"):
            raise ValidationError("O custo unitario nao pode ser negativo.")

        saldo_anterior = item.saldo_atual
        custo_total_anterior = saldo_anterior * item.custo_medio
        custo_total_entrada = quantidade * custo_unitario
        saldo_posterior = saldo_anterior + quantidade
        custo_medio = (
            (custo_total_anterior + custo_total_entrada) / saldo_posterior
            if saldo_posterior > QTD_ZERO
            else Decimal("0.0000")
        )

        item.saldo_atual = saldo_posterior
        item.custo_medio = custo_medio
        item.ultimo_preco_pago = custo_unitario
        item.save(update_fields=["saldo_atual", "custo_medio", "ultimo_preco_pago", "atualizado_em"])

        return MovimentoEstoque.objects.create(
            item=item,
            tipo=MovimentoEstoque.Tipo.PRODUCAO_RESULTADO,
            quantidade=quantidade,
            custo_unitario=custo_unitario,
            custo_total=custo_total_entrada,
            saldo_anterior=saldo_anterior,
            saldo_posterior=saldo_posterior,
            documento=documento,
            observacao=observacao or "",
        )
