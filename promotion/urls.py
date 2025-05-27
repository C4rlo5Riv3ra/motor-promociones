from django.urls import path
from .views import *

urlpatterns = [
    path('evaluar/', EvaluarPromocionesView.as_view(), name='evaluar-promociones'),
    path('pedidos/', ListaPedidosView.as_view(), name='listar_pedidos'),
]
