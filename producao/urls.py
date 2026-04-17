from django.urls import path
from . import views

urlpatterns = [
    path('lancamento/', views.lancamento_view, name='lancamento'),
    path('calcular-rendimento/', views.calcular_rendimento_parcial, name='calcular_rendimento_parcial'),
]
