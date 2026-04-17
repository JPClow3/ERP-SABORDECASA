from django.db import models

class Insumo(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome")
    unidade_medida = models.CharField(max_length=20, verbose_name="Unidade de Medida")
    preco_atual_kg = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço atual por KG")

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Insumo"
        verbose_name_plural = "Insumos"

class ProducaoDiaria(models.Model):
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE, verbose_name="Insumo")
    peso_bruto_utilizado = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Peso Bruto (kg)")
    marmitas_produzidas = models.IntegerField(verbose_name="Marmitas Produzidas")
    custo_por_marmita_calculado = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Custo por Marmita")
    data = models.DateField(auto_now_add=True, verbose_name="Data")

    def __str__(self):
        return f"Produção {self.id} - {self.insumo.nome} - {self.data}"

    class Meta:
        verbose_name = "Produção Diária"
        verbose_name_plural = "Produções Diárias"
