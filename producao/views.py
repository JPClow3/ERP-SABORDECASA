from decimal import Decimal, InvalidOperation

from django.shortcuts import get_object_or_404, render

from .models import Insumo, ProducaoDiaria


def _calcular_custo(insumo, peso_bruto, marmitas):
    custo_total = peso_bruto * insumo.preco_atual_kg
    return custo_total / Decimal(marmitas)

def lancamento_view(request):
    insumos = Insumo.objects.all()

    if request.method == "POST":
        insumo_id = request.POST.get('insumo')
        peso_bruto = request.POST.get('peso_bruto_utilizado')
        marmitas = request.POST.get('marmitas_produzidas')

        if not all([insumo_id, peso_bruto, marmitas]):
            return render(
                request,
                'producao/lancamento.html',
                {
                    'insumos': insumos,
                    'erro_form': 'Preencha todos os campos para salvar o lançamento.',
                },
            )

        try:
            insumo = get_object_or_404(Insumo, id=insumo_id)
            peso_bruto = Decimal(peso_bruto)
            marmitas = int(marmitas)
        except (InvalidOperation, TypeError, ValueError):
            return render(
                request,
                'producao/lancamento.html',
                {
                    'insumos': insumos,
                    'erro_form': 'Valores inválidos para salvar o lançamento.',
                },
            )

        if peso_bruto <= 0 or marmitas <= 0:
            return render(
                request,
                'producao/lancamento.html',
                {
                    'insumos': insumos,
                    'erro_form': 'Peso bruto e marmitas produzidas devem ser maiores que zero.',
                },
            )

        custo_por_marmita = _calcular_custo(insumo, peso_bruto, marmitas)

        ProducaoDiaria.objects.create(
            insumo=insumo,
            peso_bruto_utilizado=peso_bruto,
            marmitas_produzidas=marmitas,
            custo_por_marmita_calculado=custo_por_marmita,
        )

        return render(
            request,
            'producao/lancamento.html',
            {
                'insumos': insumos,
                'sucesso_form': 'Lançamento salvo com sucesso.',
            },
        )

    return render(request, 'producao/lancamento.html', {'insumos': insumos})

def calcular_rendimento_parcial(request):
    if request.method == "POST":
        insumo_id = request.POST.get('insumo')
        peso_bruto = request.POST.get('peso_bruto_utilizado')
        marmitas = request.POST.get('marmitas_produzidas')

        if not all([insumo_id, peso_bruto, marmitas]):
            return render(request, 'producao/partials/resultado_calculo.html', {'erro': 'Preencha todos os campos.'})

        try:
            insumo = get_object_or_404(Insumo, id=insumo_id)
            peso_bruto = Decimal(peso_bruto)
            marmitas = int(marmitas)
        except (InvalidOperation, TypeError, ValueError):
            return render(request, 'producao/partials/resultado_calculo.html', {'erro': 'Valores inválidos para cálculo.'})

        if peso_bruto <= 0:
            return render(request, 'producao/partials/resultado_calculo.html', {'erro': 'Peso bruto deve ser maior que zero.'})

        if marmitas <= 0:
            return render(request, 'producao/partials/resultado_calculo.html', {'erro': 'Quantidade de marmitas deve ser maior que zero.'})

        custo_por_marmita = _calcular_custo(insumo, peso_bruto, marmitas)

        context = {
            'custo_por_marmita': custo_por_marmita,
            'alerta_vermelho': custo_por_marmita > Decimal('6.00'),
        }
        return render(request, 'producao/partials/resultado_calculo.html', context)

    return render(request, 'producao/partials/resultado_calculo.html', {'erro': 'Método inválido.'})
