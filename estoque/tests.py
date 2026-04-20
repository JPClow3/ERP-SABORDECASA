from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import ItemEstoque, MovimentoEstoque
from .services import registrar_entrada_mercadoria, registrar_saida_estoque


class EstoqueServicesTests(TestCase):
    def test_entrada_recalcula_custo_medio_ponderado(self):
        arroz = ItemEstoque.objects.create(
            nome="Arroz Branco",
            categoria=ItemEstoque.Categoria.ARROZ,
            tipo=ItemEstoque.Tipo.INSUMO,
            unidade_medida=ItemEstoque.Unidade.KG,
        )

        registrar_entrada_mercadoria(
            fornecedor="Fornecedor A",
            itens=[
                {"item": arroz, "quantidade": Decimal("10.000"), "preco_unitario": Decimal("5.00")},
            ],
        )
        registrar_entrada_mercadoria(
            fornecedor="Fornecedor B",
            itens=[
                {"item": arroz, "quantidade": Decimal("5.000"), "preco_unitario": Decimal("8.00")},
            ],
        )

        arroz.refresh_from_db()
        self.assertEqual(arroz.saldo_atual, Decimal("15.000"))
        self.assertEqual(arroz.custo_medio, Decimal("6.0000"))
        self.assertEqual(arroz.ultimo_preco_pago, Decimal("8.0000"))
        self.assertEqual(
            MovimentoEstoque.objects.filter(item=arroz, tipo=MovimentoEstoque.Tipo.ENTRADA).count(),
            2,
        )

    def test_saida_baixa_saldo_sem_alterar_custo_medio(self):
        feijao = ItemEstoque.objects.create(
            nome="Feijao Carioca",
            categoria=ItemEstoque.Categoria.FEIJAO,
            tipo=ItemEstoque.Tipo.INSUMO,
            unidade_medida=ItemEstoque.Unidade.KG,
            saldo_atual=Decimal("8.000"),
            custo_medio=Decimal("7.2500"),
        )

        movimento = registrar_saida_estoque(
            item=feijao,
            quantidade=Decimal("2.500"),
            tipo=MovimentoEstoque.Tipo.SAIDA,
            observacao="Venda manual",
        )

        feijao.refresh_from_db()
        self.assertEqual(feijao.saldo_atual, Decimal("5.500"))
        self.assertEqual(feijao.custo_medio, Decimal("7.2500"))
        self.assertEqual(movimento.custo_total, Decimal("18.1250"))

    def test_saida_bloqueia_estoque_negativo(self):
        carne = ItemEstoque.objects.create(
            nome="Frango em Cubos",
            categoria=ItemEstoque.Categoria.CARNE,
            tipo=ItemEstoque.Tipo.INSUMO,
            unidade_medida=ItemEstoque.Unidade.KG,
            saldo_atual=Decimal("1.000"),
            custo_medio=Decimal("18.9000"),
        )

        with self.assertRaises(ValidationError):
            registrar_saida_estoque(
                item=carne,
                quantidade=Decimal("1.500"),
                tipo=MovimentoEstoque.Tipo.SAIDA,
                observacao="Tentativa invalida",
            )

        carne.refresh_from_db()
        self.assertEqual(carne.saldo_atual, Decimal("1.000"))


class EstoqueHtmxViewsTests(TestCase):
    def test_painel_estoque_renderiza_operacoes_principais(self):
        response = self.client.get(reverse("estoque:painel"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Estoque e produ")
        self.assertContains(response, "Registrar entrada")
        self.assertContains(response, "Registrar perda")

    def test_htmx_registra_entrada_e_devolve_painel_atualizado(self):
        arroz = ItemEstoque.objects.create(
            nome="Arroz Branco",
            categoria=ItemEstoque.Categoria.ARROZ,
            tipo=ItemEstoque.Tipo.INSUMO,
            unidade_medida=ItemEstoque.Unidade.KG,
        )

        response = self.client.post(
            reverse("estoque:registrar_entrada"),
            {"item": arroz.pk, "quantidade": "3.500", "preco_unitario": "6.25"},
            HTTP_HX_REQUEST="true",
        )

        arroz.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Entrada de mercadoria registrada.")
        self.assertEqual(arroz.saldo_atual, Decimal("3.500"))
        self.assertEqual(arroz.custo_medio, Decimal("6.2500"))
