import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


def migrar_insumos_legados(apps, schema_editor):
    ItemEstoque = apps.get_model("estoque", "ItemEstoque")
    Insumo = apps.get_model("producao", "Insumo")

    def categoria_para(nome):
        nome_normalizado = nome.lower()
        if "arroz" in nome_normalizado:
            return "ARROZ"
        if "feij" in nome_normalizado:
            return "FEIJAO"
        if any(chave in nome_normalizado for chave in ["carne", "frango", "bife", "porco"]):
            return "CARNE"
        return "OUTRO"

    for insumo in Insumo.objects.all():
        unidade = (insumo.unidade_medida or "kg").lower()
        if unidade not in {"kg", "g", "un", "l", "ml"}:
            unidade = "kg"

        ItemEstoque.objects.get_or_create(
            nome=insumo.nome,
            defaults={
                "categoria": categoria_para(insumo.nome),
                "tipo": "INSUMO",
                "unidade_medida": unidade,
                "saldo_atual": 0,
                "custo_medio": insumo.preco_atual_kg,
                "ultimo_preco_pago": insumo.preco_atual_kg,
                "ativo": True,
            },
        )


def desfazer_migracao_insumos_legados(apps, schema_editor):
    ItemEstoque = apps.get_model("estoque", "ItemEstoque")
    Insumo = apps.get_model("producao", "Insumo")
    nomes_legados = list(Insumo.objects.values_list("nome", flat=True))
    ItemEstoque.objects.filter(nome__in=nomes_legados, movimentos__isnull=True).delete()


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("producao", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="EntradaMercadoria",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("fornecedor", models.CharField(blank=True, max_length=120, verbose_name="Fornecedor")),
                ("data", models.DateField(default=django.utils.timezone.localdate, verbose_name="Data")),
                ("observacao", models.TextField(blank=True, verbose_name="Observacao")),
                ("criado_em", models.DateTimeField(auto_now_add=True, verbose_name="Criado em")),
            ],
            options={
                "verbose_name": "Entrada de mercadoria",
                "verbose_name_plural": "Entradas de mercadoria",
                "ordering": ["-data", "-id"],
            },
        ),
        migrations.CreateModel(
            name="ItemEstoque",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=120, unique=True, verbose_name="Nome")),
                (
                    "categoria",
                    models.CharField(
                        choices=[
                            ("ARROZ", "Arroz"),
                            ("FEIJAO", "Feijao"),
                            ("CARNE", "Carne"),
                            ("VERDURA_LEGUME", "Verduras e legumes"),
                            ("BEBIDA", "Bebida"),
                            ("EMBALAGEM", "Embalagem"),
                            ("PRODUTO_PRONTO", "Produto pronto"),
                            ("OUTRO", "Outro"),
                        ],
                        default="OUTRO",
                        max_length=30,
                        verbose_name="Categoria",
                    ),
                ),
                (
                    "tipo",
                    models.CharField(
                        choices=[
                            ("INSUMO", "Insumo"),
                            ("BEBIDA", "Bebida"),
                            ("PRODUTO_PRONTO", "Produto pronto"),
                            ("EMBALAGEM", "Embalagem"),
                            ("OUTRO", "Outro"),
                        ],
                        default="INSUMO",
                        max_length=30,
                        verbose_name="Tipo",
                    ),
                ),
                (
                    "unidade_medida",
                    models.CharField(
                        choices=[("kg", "kg"), ("g", "g"), ("un", "un"), ("l", "l"), ("ml", "ml")],
                        default="kg",
                        max_length=10,
                        verbose_name="Unidade de medida",
                    ),
                ),
                ("saldo_atual", models.DecimalField(decimal_places=3, default=0, max_digits=12, verbose_name="Saldo atual")),
                ("custo_medio", models.DecimalField(decimal_places=4, default=0, max_digits=12, verbose_name="Custo medio")),
                ("ultimo_preco_pago", models.DecimalField(decimal_places=4, default=0, max_digits=12, verbose_name="Ultimo preco pago")),
                ("ativo", models.BooleanField(default=True, verbose_name="Ativo")),
                ("criado_em", models.DateTimeField(auto_now_add=True, verbose_name="Criado em")),
                ("atualizado_em", models.DateTimeField(auto_now=True, verbose_name="Atualizado em")),
            ],
            options={
                "verbose_name": "Item de estoque",
                "verbose_name_plural": "Itens de estoque",
                "ordering": ["nome"],
            },
        ),
        migrations.CreateModel(
            name="ItemEntradaMercadoria",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantidade", models.DecimalField(decimal_places=3, max_digits=12, verbose_name="Quantidade")),
                ("preco_unitario", models.DecimalField(decimal_places=4, max_digits=12, verbose_name="Preco unitario")),
                ("custo_total", models.DecimalField(decimal_places=4, max_digits=12, verbose_name="Custo total")),
                (
                    "entrada",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="itens",
                        to="estoque.entradamercadoria",
                        verbose_name="Entrada",
                    ),
                ),
                ("item", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="estoque.itemestoque", verbose_name="Item")),
            ],
            options={
                "verbose_name": "Item da entrada",
                "verbose_name_plural": "Itens da entrada",
            },
        ),
        migrations.CreateModel(
            name="MovimentoEstoque",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "tipo",
                    models.CharField(
                        choices=[
                            ("ENTRADA", "Entrada"),
                            ("SAIDA", "Saida"),
                            ("PERDA_TECNICA", "Perda tecnica"),
                            ("PRODUCAO_CONSUMO", "Consumo de producao"),
                            ("PRODUCAO_RESULTADO", "Resultado de producao"),
                            ("AJUSTE", "Ajuste"),
                        ],
                        max_length=30,
                        verbose_name="Tipo",
                    ),
                ),
                ("quantidade", models.DecimalField(decimal_places=3, max_digits=12, verbose_name="Quantidade")),
                ("custo_unitario", models.DecimalField(decimal_places=4, max_digits=12, verbose_name="Custo unitario")),
                ("custo_total", models.DecimalField(decimal_places=4, max_digits=12, verbose_name="Custo total")),
                ("saldo_anterior", models.DecimalField(decimal_places=3, max_digits=12, verbose_name="Saldo anterior")),
                ("saldo_posterior", models.DecimalField(decimal_places=3, max_digits=12, verbose_name="Saldo posterior")),
                ("documento", models.CharField(blank=True, max_length=80, verbose_name="Documento")),
                ("observacao", models.TextField(blank=True, verbose_name="Observacao")),
                ("criado_em", models.DateTimeField(auto_now_add=True, verbose_name="Criado em")),
                (
                    "item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="movimentos",
                        to="estoque.itemestoque",
                        verbose_name="Item",
                    ),
                ),
            ],
            options={
                "verbose_name": "Movimento de estoque",
                "verbose_name_plural": "Movimentos de estoque",
                "ordering": ["-criado_em", "-id"],
            },
        ),
        migrations.RunPython(migrar_insumos_legados, desfazer_migracao_insumos_legados),
    ]
