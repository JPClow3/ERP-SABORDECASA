import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("estoque", "0001_initial"),
        ("producao", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="insumo",
            options={"verbose_name": "Insumo legado", "verbose_name_plural": "Insumos legados"},
        ),
        migrations.AlterModelOptions(
            name="producaodiaria",
            options={"verbose_name": "Producao diaria legada", "verbose_name_plural": "Producoes diarias legadas"},
        ),
        migrations.AlterField(
            model_name="insumo",
            name="preco_atual_kg",
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name="Preco atual por KG"),
        ),
        migrations.CreateModel(
            name="Produto",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=120, unique=True, verbose_name="Nome")),
                ("custo_estimado", models.DecimalField(decimal_places=4, default=0, max_digits=12, verbose_name="Custo estimado")),
                ("preco_venda", models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name="Preco de venda")),
                ("ativo", models.BooleanField(default=True, verbose_name="Ativo")),
                (
                    "item_estoque",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="produto",
                        to="estoque.itemestoque",
                        verbose_name="Item de estoque",
                    ),
                ),
            ],
            options={
                "verbose_name": "Produto",
                "verbose_name_plural": "Produtos",
                "ordering": ["nome"],
            },
        ),
        migrations.CreateModel(
            name="RegistroProducao",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("data", models.DateField(default=django.utils.timezone.localdate, verbose_name="Data")),
                ("quantidade_produzida", models.DecimalField(decimal_places=3, max_digits=12, verbose_name="Quantidade produzida")),
                ("custo_total", models.DecimalField(decimal_places=4, default=0, max_digits=12, verbose_name="Custo total")),
                ("custo_unitario", models.DecimalField(decimal_places=4, default=0, max_digits=12, verbose_name="Custo unitario")),
                ("observacao", models.TextField(blank=True, verbose_name="Observacao")),
                ("criado_em", models.DateTimeField(auto_now_add=True, verbose_name="Criado em")),
                (
                    "produto",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="producao.produto", verbose_name="Produto"),
                ),
            ],
            options={
                "verbose_name": "Registro de producao",
                "verbose_name_plural": "Registros de producao",
                "ordering": ["-data", "-id"],
            },
        ),
        migrations.CreateModel(
            name="ItemFichaTecnica",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantidade_padrao", models.DecimalField(decimal_places=3, max_digits=12, verbose_name="Quantidade padrao")),
                ("item", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="estoque.itemestoque", verbose_name="Item")),
                (
                    "produto",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="itens_ficha",
                        to="producao.produto",
                        verbose_name="Produto",
                    ),
                ),
            ],
            options={
                "verbose_name": "Item da ficha tecnica",
                "verbose_name_plural": "Itens da ficha tecnica",
                "unique_together": {("produto", "item")},
            },
        ),
        migrations.CreateModel(
            name="RegistroProducaoItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantidade_utilizada", models.DecimalField(decimal_places=3, max_digits=12, verbose_name="Quantidade utilizada")),
                ("custo_unitario", models.DecimalField(decimal_places=4, max_digits=12, verbose_name="Custo unitario")),
                ("custo_total", models.DecimalField(decimal_places=4, max_digits=12, verbose_name="Custo total")),
                ("item", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="estoque.itemestoque", verbose_name="Item")),
                (
                    "registro",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="itens",
                        to="producao.registroproducao",
                        verbose_name="Registro",
                    ),
                ),
            ],
            options={
                "verbose_name": "Item usado na producao",
                "verbose_name_plural": "Itens usados na producao",
            },
        ),
    ]
