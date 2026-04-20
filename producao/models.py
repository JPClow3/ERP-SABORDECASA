from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from estoque.models import ItemEstoque


class Insumo(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome")
    unidade_medida = models.CharField(max_length=20, verbose_name="Unidade de Medida")
    preco_atual_kg = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preco atual por KG")

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Insumo legado"
        verbose_name_plural = "Insumos legados"


class ProducaoDiaria(models.Model):
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE, verbose_name="Insumo")
    peso_bruto_utilizado = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Peso Bruto (kg)")
    marmitas_produzidas = models.IntegerField(verbose_name="Marmitas Produzidas")
    custo_por_marmita_calculado = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Custo por Marmita")
    data = models.DateField(auto_now_add=True, verbose_name="Data")

    def __str__(self):
        return f"Producao {self.id} - {self.insumo.nome} - {self.data}"

    class Meta:
        verbose_name = "Producao diaria legada"
        verbose_name_plural = "Producoes diarias legadas"


class Produto(models.Model):
    nome = models.CharField(max_length=120, unique=True, verbose_name="Nome")
    item_estoque = models.OneToOneField(
        ItemEstoque,
        on_delete=models.PROTECT,
        related_name="produto",
        verbose_name="Item de estoque",
    )
    custo_estimado = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal("0.0000"),
        verbose_name="Custo estimado",
    )
    preco_venda = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Preco de venda",
    )
    ativo = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        ordering = ["nome"]
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"

    def __str__(self):
        return self.nome

    def clean(self):
        if self.item_estoque_id and self.item_estoque.tipo != ItemEstoque.Tipo.PRODUTO_PRONTO:
            raise ValidationError({"item_estoque": "O item vinculado deve ser do tipo produto pronto."})

    def recalcular_custo_estimado(self):
        custo = sum(
            (item.quantidade_padrao * item.item.custo_medio for item in self.itens_ficha.select_related("item")),
            Decimal("0.0000"),
        )
        self.custo_estimado = custo
        self.save(update_fields=["custo_estimado"])
        return custo


class ItemFichaTecnica(models.Model):
    produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE,
        related_name="itens_ficha",
        verbose_name="Produto",
    )
    item = models.ForeignKey(ItemEstoque, on_delete=models.PROTECT, verbose_name="Item")
    quantidade_padrao = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        verbose_name="Quantidade padrao",
    )

    class Meta:
        unique_together = ("produto", "item")
        verbose_name = "Item da ficha tecnica"
        verbose_name_plural = "Itens da ficha tecnica"

    def __str__(self):
        return f"{self.produto} - {self.item}"

    def clean(self):
        if self.quantidade_padrao <= Decimal("0.000"):
            raise ValidationError({"quantidade_padrao": "A quantidade deve ser maior que zero."})
        if self.item_id and self.item.tipo == ItemEstoque.Tipo.PRODUTO_PRONTO:
            raise ValidationError({"item": "A ficha tecnica deve usar insumos, bebidas ou embalagens."})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.produto.recalcular_custo_estimado()

    def delete(self, *args, **kwargs):
        produto = self.produto
        result = super().delete(*args, **kwargs)
        produto.recalcular_custo_estimado()
        return result


class RegistroProducao(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT, verbose_name="Produto")
    data = models.DateField(default=timezone.localdate, verbose_name="Data")
    quantidade_produzida = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        verbose_name="Quantidade produzida",
    )
    custo_total = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal("0.0000"),
        verbose_name="Custo total",
    )
    custo_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal("0.0000"),
        verbose_name="Custo unitario",
    )
    observacao = models.TextField(blank=True, verbose_name="Observacao")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        ordering = ["-data", "-id"]
        verbose_name = "Registro de producao"
        verbose_name_plural = "Registros de producao"

    def __str__(self):
        return f"{self.produto} - {self.quantidade_produzida} em {self.data}"


class RegistroProducaoItem(models.Model):
    registro = models.ForeignKey(
        RegistroProducao,
        on_delete=models.CASCADE,
        related_name="itens",
        verbose_name="Registro",
    )
    item = models.ForeignKey(ItemEstoque, on_delete=models.PROTECT, verbose_name="Item")
    quantidade_utilizada = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        verbose_name="Quantidade utilizada",
    )
    custo_unitario = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        verbose_name="Custo unitario",
    )
    custo_total = models.DecimalField(max_digits=12, decimal_places=4, verbose_name="Custo total")

    class Meta:
        verbose_name = "Item usado na producao"
        verbose_name_plural = "Itens usados na producao"

    def __str__(self):
        return f"{self.item} - {self.quantidade_utilizada}"
