from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import (
    Insumo,
    ItemFichaTecnica,
    Produto,
    ProducaoDiaria,
    RegistroProducao,
    RegistroProducaoItem,
)


class ItemFichaTecnicaInline(TabularInline):
    model = ItemFichaTecnica
    extra = 1
    autocomplete_fields = ["item"]


class RegistroProducaoItemInline(TabularInline):
    model = RegistroProducaoItem
    extra = 0
    autocomplete_fields = ["item"]
    readonly_fields = ["item", "quantidade_utilizada", "custo_unitario", "custo_total"]
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Produto)
class ProdutoAdmin(ModelAdmin):
    list_display = ["nome", "item_estoque", "custo_estimado", "preco_venda", "ativo"]
    list_filter = ["ativo"]
    search_fields = ["nome", "item_estoque__nome"]
    autocomplete_fields = ["item_estoque"]
    inlines = [ItemFichaTecnicaInline]


@admin.register(RegistroProducao)
class RegistroProducaoAdmin(ModelAdmin):
    list_display = ["id", "produto", "data", "quantidade_produzida", "custo_total", "custo_unitario"]
    list_filter = ["data", "produto"]
    search_fields = ["produto__nome", "observacao"]
    readonly_fields = ["custo_total", "custo_unitario", "criado_em"]
    autocomplete_fields = ["produto"]
    inlines = [RegistroProducaoItemInline]


@admin.register(Insumo)
class InsumoAdmin(ModelAdmin):
    list_display = ["nome", "unidade_medida", "preco_atual_kg"]
    search_fields = ["nome"]


@admin.register(ProducaoDiaria)
class ProducaoDiariaAdmin(ModelAdmin):
    list_display = ["insumo", "peso_bruto_utilizado", "marmitas_produzidas", "custo_por_marmita_calculado", "data"]
    list_filter = ["data"]
