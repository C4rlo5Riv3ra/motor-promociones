from django.urls import path
from .views import PedidoListView

urlpatterns = [
    path('', PedidoListView.as_view(), name='pedido-list')
]
