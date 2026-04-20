from decimal import Decimal

from django.db import models
from django.utils import timezone


class ItemEstoque(models.Model):
    class Categoria(models.TextChoices):
        ARROZ = "ARROZ", "Arroz"
        FEIJAO = "FEIJAO", "Feijao"
        CARNE = "CARNE", "Carne"
        VERDURA_LEGUME = "VERDURA_LEGUME", "Verduras e legumes"
        BEBIDA = "BEBIDA", "Bebida"
        EMBALAGEM = "EMBALAGEM", "Embalagem"
        PRODUTO_PRONTO = "PRODUTO_PRONTO", "Produto pronto"
        OUTRO = "OUTRO", "Outro"

    class Tipo(models.TextChoices):
        INSUMO = "INSUMO", "Insumo"
        BEBIDA = "BEBIDA", "Bebida"
        PRODUTO_PRONTO = "PRODUTO_PRONTO", "Produto pronto"
        EMBALAGEM = "EMBALAGEM", "Embalagem"
        OUTRO = "OUTRO", "Outro"

    class Unidade(models.TextChoices):
        KG = "kg", "kg"
        GRAMA = "g", "g"
        UNIDADE = "un", "un"
        LITRO = "l", "l"
        MILILITRO = "ml", "ml"

    nome = models.CharField(max_length=120, unique=True, verbose_name="Nome")
    categoria = models.CharField(
        max_length=30,
        choices=Categoria.choices,
        default=Categoria.OUTRO,
        verbose_name="Categoria",
    )
    tipo = models.CharField(
        max_length=30,
        choices=Tipo.choices,
        default=Tipo.INSUMO,
        verbose_name="Tipo",
    )
    unidade_medida = models.CharField(
        max_length=10,
        choices=Unidade.choices,
        default=Unidade.KG,
        verbose_name="Unidade de medida",
    )
    saldo_atual = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        default=Decimal("0.000"),
        verbose_name="Saldo atual",
    )
    custo_medio = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal("0.0000"),
        verbose_name="Custo medio",
    )
    ultimo_preco_pago = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=Decimal("0.0000"),
        verbose_name="Ultimo preco pago",
    )
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        ordering = ["nome"]
        verbose_name = "Item de estoque"
        verbose_name_plural = "Itens de estoque"

    def __str__(self):
        return self.nome


class EntradaMercadoria(models.Model):
    fornecedor = models.CharField(max_length=120, blank=True, verbose_name="Fornecedor")
    data = models.DateField(default=timezone.localdate, verbose_name="Data")
    observacao = models.TextField(blank=True, verbose_name="Observacao")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        ordering = ["-data", "-id"]
        verbose_name = "Entrada de mercadoria"
        verbose_name_plural = "Entradas de mercadoria"

    def __str__(self):
        return f"Entrada #{self.pk} - {self.data}"

    @property
    def custo_total(self):
        return sum((item.custo_total for item in self.itens.all()), Decimal("0.0000"))


class ItemEntradaMercadoria(models.Model):
    entrada = models.ForeignKey(
        EntradaMercadoria,
        on_delete=models.CASCADE,
        related_name="itens",
        verbose_name="Entrada",
    )
    item = models.ForeignKey(ItemEstoque, on_delete=models.PROTECT, verbose_name="Item")
    quantidade = models.DecimalField(max_digits=12, decimal_places=3, verbose_name="Quantidade")
    preco_unitario = models.DecimalField(max_digits=12, decimal_places=4, verbose_name="Preco unitario")
    custo_total = models.DecimalField(max_digits=12, decimal_places=4, verbose_name="Custo total")

    class Meta:
        verbose_name = "Item da entrada"
        verbose_name_plural = "Itens da entrada"

    def __str__(self):
        return f"{self.item} - {self.quantidade} {self.item.unidade_medida}"

    def save(self, *args, **kwargs):
        self.custo_total = self.quantidade * self.preco_unitario
        super().save(*args, **kwargs)


class MovimentoEstoque(models.Model):
    class Tipo(models.TextChoices):
        ENTRADA = "ENTRADA", "Entrada"
        SAIDA = "SAIDA", "Saida"
        PERDA_TECNICA = "PERDA_TECNICA", "Perda tecnica"
        PRODUCAO_CONSUMO = "PRODUCAO_CONSUMO", "Consumo de producao"
        PRODUCAO_RESULTADO = "PRODUCAO_RESULTADO", "Resultado de producao"
        AJUSTE = "AJUSTE", "Ajuste"

    item = models.ForeignKey(
        ItemEstoque,
        on_delete=models.PROTECT,
        related_name="movimentos",
        verbose_name="Item",
    )
    tipo = models.CharField(max_length=30, choices=Tipo.choices, verbose_name="Tipo")
    quantidade = models.DecimalField(max_digits=12, decimal_places=3, verbose_name="Quantidade")
    custo_unitario = models.DecimalField(max_digits=12, decimal_places=4, verbose_name="Custo unitario")
    custo_total = models.DecimalField(max_digits=12, decimal_places=4, verbose_name="Custo total")
    saldo_anterior = models.DecimalField(max_digits=12, decimal_places=3, verbose_name="Saldo anterior")
    saldo_posterior = models.DecimalField(max_digits=12, decimal_places=3, verbose_name="Saldo posterior")
    documento = models.CharField(max_length=80, blank=True, verbose_name="Documento")
    observacao = models.TextField(blank=True, verbose_name="Observacao")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        ordering = ["-criado_em", "-id"]
        verbose_name = "Movimento de estoque"
        verbose_name_plural = "Movimentos de estoque"

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.item} - {self.quantidade}"
