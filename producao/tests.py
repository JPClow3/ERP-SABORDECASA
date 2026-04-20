from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase

from estoque.models import ItemEstoque, MovimentoEstoque
from .models import ItemFichaTecnica, Produto
from .services import registrar_producao


class RegistroProducaoTests(TestCase):
    def test_producao_baixa_insumos_e_gera_produto_pronto(self):
        arroz = ItemEstoque.objects.create(
            nome="Arroz Branco",
            categoria=ItemEstoque.Categoria.ARROZ,
            tipo=ItemEstoque.Tipo.INSUMO,
            unidade_medida=ItemEstoque.Unidade.KG,
            saldo_atual=Decimal("10.000"),
            custo_medio=Decimal("5.5000"),
        )
        feijao = ItemEstoque.objects.create(
            nome="Feijao Carioca",
            categoria=ItemEstoque.Categoria.FEIJAO,
            tipo=ItemEstoque.Tipo.INSUMO,
            unidade_medida=ItemEstoque.Unidade.KG,
            saldo_atual=Decimal("8.000"),
            custo_medio=Decimal("8.2000"),
        )
        marmita_item = ItemEstoque.objects.create(
            nome="Marmita Media",
            categoria=ItemEstoque.Categoria.PRODUTO_PRONTO,
            tipo=ItemEstoque.Tipo.PRODUTO_PRONTO,
            unidade_medida=ItemEstoque.Unidade.UNIDADE,
        )
        produto = Produto.objects.create(nome="Marmita Media", item_estoque=marmita_item)
        ItemFichaTecnica.objects.create(produto=produto, item=arroz, quantidade_padrao=Decimal("0.180"))
        ItemFichaTecnica.objects.create(produto=produto, item=feijao, quantidade_padrao=Decimal("0.120"))

        registro = registrar_producao(produto=produto, quantidade_produzida=Decimal("10.000"))

        arroz.refresh_from_db()
        feijao.refresh_from_db()
        marmita_item.refresh_from_db()
        self.assertEqual(arroz.saldo_atual, Decimal("8.200"))
        self.assertEqual(feijao.saldo_atual, Decimal("6.800"))
        self.assertEqual(marmita_item.saldo_atual, Decimal("10.000"))
        self.assertEqual(registro.custo_total, Decimal("19.7400"))
        self.assertEqual(registro.custo_unitario, Decimal("1.9740"))
        self.assertEqual(
            MovimentoEstoque.objects.filter(tipo=MovimentoEstoque.Tipo.PRODUCAO_CONSUMO).count(),
            2,
        )
        self.assertEqual(
            MovimentoEstoque.objects.filter(tipo=MovimentoEstoque.Tipo.PRODUCAO_RESULTADO).count(),
            1,
        )

    def test_producao_bloqueia_quando_insumo_nao_tem_saldo(self):
        arroz = ItemEstoque.objects.create(
            nome="Arroz Branco",
            categoria=ItemEstoque.Categoria.ARROZ,
            tipo=ItemEstoque.Tipo.INSUMO,
            unidade_medida=ItemEstoque.Unidade.KG,
            saldo_atual=Decimal("1.000"),
            custo_medio=Decimal("5.5000"),
        )
        marmita_item = ItemEstoque.objects.create(
            nome="Marmita Grande",
            categoria=ItemEstoque.Categoria.PRODUTO_PRONTO,
            tipo=ItemEstoque.Tipo.PRODUTO_PRONTO,
            unidade_medida=ItemEstoque.Unidade.UNIDADE,
        )
        produto = Produto.objects.create(nome="Marmita Grande", item_estoque=marmita_item)
        ItemFichaTecnica.objects.create(produto=produto, item=arroz, quantidade_padrao=Decimal("0.300"))

        with self.assertRaises(ValidationError):
            registrar_producao(produto=produto, quantidade_produzida=Decimal("5.000"))

        arroz.refresh_from_db()
        marmita_item.refresh_from_db()
        self.assertEqual(arroz.saldo_atual, Decimal("1.000"))
        self.assertEqual(marmita_item.saldo_atual, Decimal("0.000"))
