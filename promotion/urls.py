from django.urls import path
# primero hay que importar las vistas que se van a usar
from views import EvaluarPromocionesView, PromocionListAPIView

urlpatterns = [
    path('promociones/calcular/', EvaluarPromocionesView.as_view(), name='calcular-promociones'),
    path('promociones/', PromocionListAPIView.as_view(), name='listar-promociones'),
]