from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from producao.models import Produto
from producao.services import registrar_producao
from .models import ItemEstoque, MovimentoEstoque
from .services import registrar_entrada_mercadoria, registrar_perda_tecnica, registrar_saida_estoque


def _decimal_from_post(request, name):
    try:
        return Decimal((request.POST.get(name) or "").replace(",", "."))
    except (InvalidOperation, AttributeError):
        raise ValidationError(f"Valor invalido para {name}.")


def _painel_context(alerta=None, erro=None):
    itens = ItemEstoque.objects.filter(ativo=True).order_by("nome")
    produtos = Produto.objects.filter(ativo=True).select_related("item_estoque").order_by("nome")
    movimentos = MovimentoEstoque.objects.select_related("item")[:12]
    resumo = {
        "total_itens": ItemEstoque.objects.filter(ativo=True).count(),
        "valor_estoque": sum((item.saldo_atual * item.custo_medio for item in itens), Decimal("0.0000")),
        "itens_sem_saldo": ItemEstoque.objects.filter(ativo=True, saldo_atual__lte=0).count(),
        "produtos": produtos.count(),
    }
    return {
        "itens": itens,
        "produtos": produtos,
        "movimentos": movimentos,
        "resumo": resumo,
        "alerta": alerta,
        "erro": erro,
    }


def _render_painel(request, *, alerta=None, erro=None):
    template = "estoque/partials/painel_conteudo.html" if request.htmx else "estoque/painel.html"
    return render(request, template, _painel_context(alerta=alerta, erro=erro))


def painel_estoque(request):
    return render(request, "estoque/painel.html", _painel_context())


def registrar_entrada(request):
    if request.method != "POST":
        return redirect("estoque:painel")

    try:
        item = get_object_or_404(ItemEstoque, pk=request.POST.get("item"))
        registrar_entrada_mercadoria(
            fornecedor=request.POST.get("fornecedor", ""),
            observacao=request.POST.get("observacao", ""),
            itens=[
                {
                    "item": item,
                    "quantidade": _decimal_from_post(request, "quantidade"),
                    "preco_unitario": _decimal_from_post(request, "preco_unitario"),
                }
            ],
        )
        return _render_painel(request, alerta="Entrada de mercadoria registrada.")
    except ValidationError as exc:
        return _render_painel(request, erro=" ".join(exc.messages))


def registrar_saida(request):
    if request.method != "POST":
        return redirect("estoque:painel")

    try:
        item = get_object_or_404(ItemEstoque, pk=request.POST.get("item"))
        registrar_saida_estoque(
            item=item,
            quantidade=_decimal_from_post(request, "quantidade"),
            tipo=MovimentoEstoque.Tipo.SAIDA,
            observacao=request.POST.get("observacao", ""),
        )
        return _render_painel(request, alerta="Saida de mercadoria registrada.")
    except ValidationError as exc:
        return _render_painel(request, erro=" ".join(exc.messages))


def registrar_perda(request):
    if request.method != "POST":
        return redirect("estoque:painel")

    try:
        item = get_object_or_404(ItemEstoque, pk=request.POST.get("item"))
        registrar_perda_tecnica(
            item=item,
            quantidade=_decimal_from_post(request, "quantidade"),
            observacao=request.POST.get("observacao", ""),
        )
        return _render_painel(request, alerta="Perda tecnica registrada.")
    except ValidationError as exc:
        return _render_painel(request, erro=" ".join(exc.messages))


def registrar_producao_view(request):
    if request.method != "POST":
        return redirect("estoque:painel")

    try:
        produto = get_object_or_404(Produto, pk=request.POST.get("produto"))
        registro = registrar_producao(
            produto=produto,
            quantidade_produzida=_decimal_from_post(request, "quantidade_produzida"),
            observacao=request.POST.get("observacao", ""),
        )
        return _render_painel(
            request,
            alerta=f"Producao registrada: {registro.quantidade_produzida} unidade(s) de {produto.nome}.",
        )
    except ValidationError as exc:
        return _render_painel(request, erro=" ".join(exc.messages))


def preview_producao(request):
    produto_id = request.POST.get("produto")
    quantidade = request.POST.get("quantidade_produzida")
    if not produto_id or not quantidade:
        return render(request, "estoque/partials/preview_producao.html", {"mensagem": "Selecione produto e quantidade."})

    try:
        produto = get_object_or_404(Produto.objects.prefetch_related("itens_ficha__item"), pk=produto_id)
        quantidade = Decimal(quantidade.replace(",", "."))
        itens = []
        custo_total = Decimal("0.0000")
        for ficha in produto.itens_ficha.all():
            qtd_necessaria = ficha.quantidade_padrao * quantidade
            custo = qtd_necessaria * ficha.item.custo_medio
            custo_total += custo
            itens.append(
                {
                    "nome": ficha.item.nome,
                    "quantidade": qtd_necessaria,
                    "saldo": ficha.item.saldo_atual,
                    "insuficiente": ficha.item.saldo_atual < qtd_necessaria,
                }
            )
        custo_unitario = custo_total / quantidade if quantidade > 0 else Decimal("0.0000")
        return render(
            request,
            "estoque/partials/preview_producao.html",
            {"produto": produto, "itens_preview": itens, "custo_total": custo_total, "custo_unitario": custo_unitario},
        )
    except (InvalidOperation, ValidationError):
        return render(request, "estoque/partials/preview_producao.html", {"erro": "Quantidade invalida."})
