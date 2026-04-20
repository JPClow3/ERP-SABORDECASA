from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.import_export.forms import ExportForm, ImportForm

from .models import EntradaMercadoria, ItemEntradaMercadoria, ItemEstoque, MovimentoEstoque


class ItemEstoqueResource(resources.ModelResource):
    class Meta:
        model = ItemEstoque
        fields = (
            "id",
            "nome",
            "categoria",
            "tipo",
            "unidade_medida",
            "saldo_atual",
            "custo_medio",
            "ultimo_preco_pago",
            "ativo",
        )


class ItemEntradaMercadoriaInline(TabularInline):
    model = ItemEntradaMercadoria
    extra = 1
    autocomplete_fields = ["item"]
    readonly_fields = ["custo_total"]


@admin.register(ItemEstoque)
class ItemEstoqueAdmin(ModelAdmin, ImportExportModelAdmin):
    resource_class = ItemEstoqueResource
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = ["nome", "categoria", "tipo", "unidade_medida", "saldo_atual", "custo_medio", "ativo"]
    list_filter = ["categoria", "tipo", "unidade_medida", "ativo"]
    search_fields = ["nome"]
    list_editable = ["ativo"]
    readonly_fields = ["criado_em", "atualizado_em"]


@admin.register(EntradaMercadoria)
class EntradaMercadoriaAdmin(ModelAdmin):
    list_display = ["id", "fornecedor", "data", "custo_total", "criado_em"]
    search_fields = ["fornecedor", "observacao"]
    list_filter = ["data"]
    inlines = [ItemEntradaMercadoriaInline]
    readonly_fields = ["criado_em"]


@admin.register(MovimentoEstoque)
class MovimentoEstoqueAdmin(ModelAdmin):
    list_display = [
        "criado_em",
        "item",
        "tipo",
        "quantidade",
        "custo_unitario",
        "custo_total",
        "saldo_anterior",
        "saldo_posterior",
    ]
    list_filter = ["tipo", "item__categoria", "criado_em"]
    search_fields = ["item__nome", "documento", "observacao"]
    readonly_fields = [
        "item",
        "tipo",
        "quantidade",
        "custo_unitario",
        "custo_total",
        "saldo_anterior",
        "saldo_posterior",
        "documento",
        "observacao",
        "criado_em",
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
