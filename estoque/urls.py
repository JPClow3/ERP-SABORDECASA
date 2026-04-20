from django.urls import path

from . import views

app_name = "estoque"

urlpatterns = [
    path("", views.painel_estoque, name="painel"),
    path("entrada/", views.registrar_entrada, name="registrar_entrada"),
    path("saida/", views.registrar_saida, name="registrar_saida"),
    path("perda/", views.registrar_perda, name="registrar_perda"),
    path("producao/", views.registrar_producao_view, name="registrar_producao"),
    path("producao/preview/", views.preview_producao, name="preview_producao"),
]
