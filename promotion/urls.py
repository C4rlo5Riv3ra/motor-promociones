from django.urls import path
from .views import EvaluarPromocionesView

urlpatterns = [
    path('evaluar/', EvaluarPromocionesView.as_view(), name='evaluar-promociones'),
]
